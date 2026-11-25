#include "bn_core.h"
#include "bn_keypad.h"
#include "bn_regular_bg_ptr.h"
#include "bn_sprite_ptr.h"

#include "bn_regular_bg_items_bg_pantano.h"
#include "bn_sprite_items_lolo.h"
#include "bn_sprite_items_lala.h"
#include "bn_sprite_items_bloco.h"
#include "bn_sprite_items_coracao.h"

namespace {
    constexpr int tile_to_x(int tx) { return -112 + tx * 16; }
    constexpr int tile_to_y(int ty) { return -72 + ty * 16; }
}

int main() {
    bn::core::init();

    bn::regular_bg_ptr bg = bn::regular_bg_items::bg_pantano.create_bg(8, 48);

    int lolo_x = 2, lolo_y = 5;
    int block_x = 5, block_y = 5;
    int heart_x = 7, heart_y = 2;
    bool heart_collected = false;

    bn::sprite_ptr lolo = bn::sprite_items::lolo.create_sprite(tile_to_x(lolo_x), tile_to_y(lolo_y));
    bn::sprite_ptr lala = bn::sprite_items::lala.create_sprite(tile_to_x(12), tile_to_y(5));
    bn::sprite_ptr bloco = bn::sprite_items::bloco.create_sprite(tile_to_x(block_x), tile_to_y(block_y));
    bn::sprite_ptr coracao = bn::sprite_items::coracao.create_sprite(tile_to_x(heart_x), tile_to_y(heart_y));

    while(true) {
        int dx = 0, dy = 0;
        if(bn::keypad::left_pressed())       dx = -1;
        else if(bn::keypad::right_pressed()) dx = 1;
        else if(bn::keypad::up_pressed())    dy = -1;
        else if(bn::keypad::down_pressed())  dy = 1;

        if(dx != 0 || dy != 0) {
            int nx = lolo_x + dx;
            int ny = lolo_y + dy;

            if(nx > 0 && nx < 14 && ny > 0 && ny < 9) {
                if(nx == block_x && ny == block_y) {
                    int bnx = block_x + dx;
                    int bny = block_y + dy;
                    if(bnx > 0 && bnx < 14 && bny > 0 && bny < 9) {
                        block_x = bnx;
                        block_y = bny;
                        lolo_x = nx;
                        lolo_y = ny;
                    }
                } else {
                    lolo_x = nx;
                    lolo_y = ny;
                }
            }
        }

        if(!heart_collected && lolo_x == heart_x && lolo_y == heart_y) {
            heart_collected = true;
            coracao.set_visible(false);
        }

        lolo.set_position(tile_to_x(lolo_x), tile_to_y(lolo_y));
        bloco.set_position(tile_to_x(block_x), tile_to_y(block_y));

        bn::core::update();
    }
}
