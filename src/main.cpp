#include "bn_core.h"
#include "bn_keypad.h"
#include "bn_optional.h"
#include "bn_vector.h"
#include "bn_regular_bg_ptr.h"
#include "bn_sprite_ptr.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_palettes.h"
#include "bn_colors.h"

#include "bn_regular_bg_items_bg_pantano.h"
#include "bn_regular_bg_items_bg_agua.h"
#include "bn_regular_bg_items_bg_lava.h"
#include "bn_regular_bg_items_bg_gelo.h"
#include "bn_sprite_items_lolo.h"
#include "bn_sprite_items_lala.h"
#include "bn_sprite_items_props.h"
#include "bn_sprite_items_enemies.h"

#include "chambers.h"

namespace {

using namespace sokoban;

constexpr int tile_to_x(int tx) { return -112 + tx * 16; }
constexpr int tile_to_y(int ty) { return -72 + ty * 16; }

struct ActiveEnemy {
    int x, y;
    int dx, dy;
    EnemyKind kind;
    bn::sprite_ptr sprite;
};

struct ActiveBlock {
    int x, y;
    bool active;
    bn::sprite_ptr sprite;
};

struct ActiveHeart {
    int x, y;
    bool collected;
    bn::sprite_ptr sprite;
};

bn::regular_bg_ptr create_chamber_bg(int chamber_idx) {
    switch(chamber_idx) {
        case 0: return bn::regular_bg_items::bg_pantano.create_bg(8, 48);
        case 1: return bn::regular_bg_items::bg_agua.create_bg(8, 48);
        case 2: return bn::regular_bg_items::bg_lava.create_bg(8, 48);
        default: return bn::regular_bg_items::bg_gelo.create_bg(8, 48);
    }
}

void fade_transition(bool fade_out) {
    for(int i = 0; i <= 15; ++i) {
        bn::fixed intensity = fade_out ? (bn::fixed(i) / 15) : (bn::fixed(15 - i) / 15);
        bn::bg_palettes::set_fade(bn::colors::black, intensity);
        bn::sprite_palettes::set_fade(bn::colors::black, intensity);
        bn::core::update();
    }
}

class Game {
public:
    void run() {
        load_chamber(0);
        fade_transition(false);

        while(true) {
            if(bn::keypad::select_pressed() || bn::keypad::r_pressed()) {
                fade_transition(true);
                load_chamber(_chamber_idx);
                fade_transition(false);
                continue;
            }
            if(bn::keypad::l_pressed()) {
                advance_chamber();
                continue;
            }

            update_animations();
            update_player();
            update_enemies();

            if(_hurt_timer > 0) {
                --_hurt_timer;
                if(_hurt_timer == 0) {
                    fade_transition(true);
                    load_chamber(_chamber_idx);
                    fade_transition(false);
                }
            }

            bn::core::update();
        }
    }

private:
    int _chamber_idx = 0;
    TileType _grid[GRID_H][GRID_W];
    bn::optional<bn::regular_bg_ptr> _bg;

    bn::optional<bn::sprite_ptr> _lolo;
    bn::optional<bn::sprite_ptr> _lala;
    bn::optional<bn::sprite_ptr> _chest;
    bn::optional<bn::sprite_ptr> _key;

    bn::vector<ActiveBlock, 6> _blocks;
    bn::vector<bn::sprite_ptr, 6> _rocks;
    bn::vector<bn::sprite_ptr, 8> _bridges;
    bn::vector<ActiveHeart, 4> _hearts;
    bn::vector<ActiveEnemy, 3> _enemies;

    int _lolo_x = 2, _lolo_y = 5;
    int _lolo_dir = 0; // 0=down, 1=up, 2=left, 3=right
    int _walk_step = 0;
    int _move_cooldown = 0;
    int _enemy_tick = 0;
    int _anim_tick = 0;
    int _hurt_timer = 0;
    bool _key_collected = false;
    bool _chest_open = false;

    void load_chamber(int idx) {
        _chamber_idx = idx % NUM_CHAMBERS;
        const ChamberDef& def = CHAMBERS[_chamber_idx];

        _bg.reset();
        _lolo.reset();
        _lala.reset();
        _chest.reset();
        _key.reset();
        _blocks.clear();
        _rocks.clear();
        _bridges.clear();
        _hearts.clear();
        _enemies.clear();

        _bg = create_chamber_bg(_chamber_idx);

        for(int y = 0; y < GRID_H; ++y) {
            for(int x = 0; x < GRID_W; ++x) {
                char c = def.map[y][x];
                if(c == '#')      _grid[y][x] = TileType::Wall;
                else if(c == '~') _grid[y][x] = TileType::Hazard;
                else if(c == 'D') _grid[y][x] = TileType::Door;
                else              _grid[y][x] = TileType::Floor;
            }
        }

        // Rochas fixas
        for(int i = 0; i < def.rock_count; ++i) {
            Pos p = def.rocks[i];
            _grid[p.y][p.x] = TileType::Wall;
            bn::sprite_ptr spr = bn::sprite_items::props.create_sprite(tile_to_x(p.x), tile_to_y(p.y), 1);
            spr.set_z_order(10);
            _rocks.push_back(bn::move(spr));
        }

        // Blocos empurraveis (pedra = 0, gelo = 3)
        int block_tile = def.ice_slides ? 3 : 0;
        for(int i = 0; i < def.block_count; ++i) {
            Pos p = def.blocks[i];
            bn::sprite_ptr spr = bn::sprite_items::props.create_sprite(tile_to_x(p.x), tile_to_y(p.y), block_tile);
            spr.set_z_order(5);
            _blocks.push_back({p.x, p.y, true, bn::move(spr)});
        }

        // Coracoes
        for(int i = 0; i < def.heart_count; ++i) {
            Pos p = def.hearts[i];
            bn::sprite_ptr spr = bn::sprite_items::props.create_sprite(tile_to_x(p.x), tile_to_y(p.y), 4);
            spr.set_z_order(8);
            _hearts.push_back({p.x, p.y, false, bn::move(spr)});
        }

        // Chave
        _key_collected = !def.has_key;
        if(def.has_key) {
            _key = bn::sprite_items::props.create_sprite(tile_to_x(def.key_pos.x), tile_to_y(def.key_pos.y), 5);
            _key->set_z_order(8);
        }

        // Bau de saida (fechado = 6, aberto = 7)
        _chest_open = false;
        _chest = bn::sprite_items::props.create_sprite(tile_to_x(def.chest_pos.x), tile_to_y(def.chest_pos.y), 6);
        _chest->set_z_order(8);

        // Lala
        _lala = bn::sprite_items::lala.create_sprite(tile_to_x(def.lala_pos.x), tile_to_y(def.lala_pos.y), 0);
        _lala->set_z_order(4);

        // Lolo
        _lolo_x = def.lolo_start.x;
        _lolo_y = def.lolo_start.y;
        _lolo_dir = 0;
        _walk_step = 0;
        _move_cooldown = 0;
        _enemy_tick = 0;
        _hurt_timer = 0;
        _lolo = bn::sprite_items::lolo.create_sprite(tile_to_x(_lolo_x), tile_to_y(_lolo_y), 0);
        _lolo->set_z_order(2);

        // Inimigos
        for(int i = 0; i < def.enemy_count; ++i) {
            const EnemyDef& e = def.enemies[i];
            int base_frame = static_cast<int>(e.kind) * 4;
            bn::sprite_ptr spr = bn::sprite_items::enemies.create_sprite(tile_to_x(e.x), tile_to_y(e.y), base_frame);
            spr.set_z_order(3);
            _enemies.push_back({e.x, e.y, e.dx, e.dy, e.kind, bn::move(spr)});
        }
    }

    int find_block(int x, int y) const {
        for(int i = 0; i < _blocks.size(); ++i) {
            if(_blocks[i].active && _blocks[i].x == x && _blocks[i].y == y) {
                return i;
            }
        }
        return -1;
    }

    bool has_enemy(int x, int y) const {
        for(const ActiveEnemy& e : _enemies) {
            if(e.x == x && e.y == y) return true;
        }
        return false;
    }

    bool can_walk_to(int x, int y) const {
        if(x < 0 || x >= GRID_W || y < 0 || y >= GRID_H) return false;
        TileType t = _grid[y][x];
        return (t == TileType::Floor || t == TileType::Bridge);
    }

    void update_player() {
        if(_hurt_timer > 0) return;
        if(_move_cooldown > 0) {
            --_move_cooldown;
            return;
        }

        int dx = 0, dy = 0;
        if(bn::keypad::left_held())       { dx = -1; _lolo_dir = 2; }
        else if(bn::keypad::right_held()) { dx = 1;  _lolo_dir = 3; }
        else if(bn::keypad::up_held())    { dy = -1; _lolo_dir = 1; }
        else if(bn::keypad::down_held())  { dy = 1;  _lolo_dir = 0; }

        if(dx == 0 && dy == 0) return;

        const ChamberDef& def = CHAMBERS[_chamber_idx];
        int nx = _lolo_x + dx;
        int ny = _lolo_y + dy;

        if(!can_walk_to(nx, ny)) {
            _lolo->set_tiles(bn::sprite_items::lolo.tiles_item(), _lolo_dir * 2);
            _move_cooldown = 8;
            return;
        }

        int blk = find_block(nx, ny);
        if(blk >= 0) {
            int bx = nx + dx;
            int by = ny + dy;

            bool blocked_by_entity = (find_block(bx, by) >= 0) || has_enemy(bx, by) ||
                                     (bx == def.lala_pos.x && by == def.lala_pos.y) ||
                                     (bx == def.chest_pos.x && by == def.chest_pos.y);

            if(bx >= 0 && bx < GRID_W && by >= 0 && by < GRID_H && !blocked_by_entity) {
                TileType dest = _grid[by][bx];
                if(dest == TileType::Hazard && def.water_bridges) {
                    // Bloco cai na agua e vira ponte!
                    _blocks[blk].active = false;
                    _blocks[blk].sprite.set_visible(false);
                    _grid[by][bx] = TileType::Bridge;
                    if(!_bridges.full()) {
                        bn::sprite_ptr br = bn::sprite_items::props.create_sprite(tile_to_x(bx), tile_to_y(by), 2);
                        br.set_z_order(12);
                        _bridges.push_back(bn::move(br));
                    }
                    _lolo_x = nx;
                    _lolo_y = ny;
                } else if(dest == TileType::Floor || dest == TileType::Bridge) {
                    // Empurra bloco (no gelo, desliza ate bater)
                    int final_x = bx, final_y = by;
                    if(def.ice_slides) {
                        while(true) {
                            int sx = final_x + dx;
                            int sy = final_y + dy;
                            if(!can_walk_to(sx, sy) || find_block(sx, sy) >= 0 || has_enemy(sx, sy) ||
                               (sx == def.lala_pos.x && sy == def.lala_pos.y) ||
                               (sx == def.chest_pos.x && sy == def.chest_pos.y)) {
                                break;
                            }
                            final_x = sx;
                            final_y = sy;
                        }
                    }
                    _blocks[blk].x = final_x;
                    _blocks[blk].y = final_y;
                    _blocks[blk].sprite.set_position(tile_to_x(final_x), tile_to_y(final_y));
                    _lolo_x = nx;
                    _lolo_y = ny;
                    _lolo->set_tiles(bn::sprite_items::lolo.tiles_item(), 8); // frame empurrando
                }
            }
        } else {
            _lolo_x = nx;
            _lolo_y = ny;
            _walk_step ^= 1;
            _lolo->set_tiles(bn::sprite_items::lolo.tiles_item(), _lolo_dir * 2 + _walk_step);
        }

        _lolo->set_position(tile_to_x(_lolo_x), tile_to_y(_lolo_y));
        _move_cooldown = 10;

        check_pickups_and_exit();
    }

    void check_pickups_and_exit() {
        const ChamberDef& def = CHAMBERS[_chamber_idx];

        bool all_hearts = true;
        for(ActiveHeart& h : _hearts) {
            if(!h.collected && h.x == _lolo_x && h.y == _lolo_y) {
                h.collected = true;
                h.sprite.set_visible(false);
            }
            if(!h.collected) all_hearts = false;
        }

        if(!_key_collected && _lolo_x == def.key_pos.x && _lolo_y == def.key_pos.y) {
            _key_collected = true;
            if(_key) _key->set_visible(false);
        }

        if(all_hearts && _key_collected && !_chest_open) {
            _chest_open = true;
            _chest->set_tiles(bn::sprite_items::props.tiles_item(), 7);
            _lala->set_tiles(bn::sprite_items::lala.tiles_item(), 2);
        }

        if(_chest_open && _lolo_x == def.chest_pos.x && _lolo_y == def.chest_pos.y) {
            advance_chamber();
        }
    }

    void update_enemies() {
        if(_hurt_timer > 0) return;

        // Checa colisao com Lolo
        for(const ActiveEnemy& e : _enemies) {
            if(e.x == _lolo_x && e.y == _lolo_y) {
                trigger_hurt();
                return;
            }
        }

        ++_enemy_tick;
        if(_enemy_tick < 28) return;
        _enemy_tick = 0;

        const ChamberDef& def = CHAMBERS[_chamber_idx];
        for(ActiveEnemy& e : _enemies) {
            int nx = e.x + e.dx;
            int ny = e.y + e.dy;

            bool blocked = !can_walk_to(nx, ny) || find_block(nx, ny) >= 0 ||
                           (nx == def.lala_pos.x && ny == def.lala_pos.y) ||
                           (nx == def.chest_pos.x && ny == def.chest_pos.y);

            if(blocked) {
                e.dx = -e.dx;
                e.dy = -e.dy;
            } else {
                e.x = nx;
                e.y = ny;
                e.sprite.set_position(tile_to_x(e.x), tile_to_y(e.y));
            }

            if(e.x == _lolo_x && e.y == _lolo_y) {
                trigger_hurt();
                return;
            }
        }
    }

    void trigger_hurt() {
        _hurt_timer = 30;
        _lolo->set_tiles(bn::sprite_items::lolo.tiles_item(), 9);
    }

    void update_animations() {
        ++_anim_tick;
        int enemy_subframe = (_anim_tick / 10) % 4;
        for(ActiveEnemy& e : _enemies) {
            int base = static_cast<int>(e.kind) * 4;
            e.sprite.set_tiles(bn::sprite_items::enemies.tiles_item(), base + enemy_subframe);
        }
        if(!_chest_open && _lala) {
            _lala->set_tiles(bn::sprite_items::lala.tiles_item(), (_anim_tick / 20) % 2);
        }
    }

    void advance_chamber() {
        fade_transition(true);
        load_chamber((_chamber_idx + 1) % NUM_CHAMBERS);
        fade_transition(false);
    }
};

} // namespace

int main() {
    bn::core::init();
    Game game;
    game.run();
    return 0;
}
