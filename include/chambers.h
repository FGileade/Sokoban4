#ifndef CHAMBERS_H
#define CHAMBERS_H

namespace sokoban {

constexpr int GRID_W = 15;
constexpr int GRID_H = 10;
constexpr int NUM_CHAMBERS = 4;

enum class TileType : unsigned char {
    Floor = 0,
    Wall = 1,
    Hazard = 2,   // Agua (camara 2) ou Lava (camara 3)
    Bridge = 3,   // Bloco empurrado na agua vira ponte
    Door = 4
};

enum class EnemyKind : unsigned char {
    Leeper = 0,   // Camara 1 (Pantano) - patrulha horizontal
    Octopus = 1,  // Camara 2 (Agua) - patrulha vertical
    Flame = 2,    // Camara 3 (Lava) - patrulha horizontal
    Spiky = 3     // Camara 4 (Gelo) - patrulha horizontal/vertical
};

struct EnemyDef {
    int x, y;
    int dx, dy;
    EnemyKind kind;
};

struct Pos {
    int x, y;
};

struct ChamberDef {
    const char* map[GRID_H];
    Pos lolo_start;
    Pos lala_pos;
    Pos chest_pos;
    bool has_key;
    Pos key_pos;
    bool ice_slides;
    bool water_bridges;
    int block_count;
    Pos blocks[6];
    int rock_count;
    Pos rocks[6];
    int heart_count;
    Pos hearts[4];
    int enemy_count;
    EnemyDef enemies[3];
};

// Legenda dos mapas: '#' parede, '.' piso, '~' agua/lava, 'D' porta topo
constexpr ChamberDef CHAMBERS[NUM_CHAMBERS] = {
    // 1. PANTANO (verde musgo): blocos de pedra, rochas fixas, leeper, coracao e chave
    {
        {
            "#######D#######",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "###############"
        },
        {2, 5}, {12, 5}, {7, 1},
        true, {12, 2},
        false, false,
        3, {{5, 5}, {7, 4}, {9, 5}, {0, 0}, {0, 0}, {0, 0}},
        2, {{2, 7}, {12, 7}, {0, 0}, {0, 0}, {0, 0}, {0, 0}},
        2, {{7, 2}, {7, 6}, {0, 0}, {0, 0}},
        1, {{5, 3, 1, 0, EnemyKind::Leeper}, {}, {}}
    },
    // 2. AGUA (azul): empurre blocos de pedra na agua para formar pontes, polvos roxos
    {
        {
            "#######D#######",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "#....~~~~~....#",
            "###############"
        },
        {2, 5}, {12, 5}, {12, 2},
        false, {0, 0},
        false, true,
        5, {{3, 4}, {3, 5}, {3, 6}, {2, 3}, {2, 7}, {0, 0}},
        0, {{0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}},
        2, {{3, 2}, {11, 7}, {0, 0}, {0, 0}},
        2, {{10, 2, 0, 1, EnemyKind::Octopus}, {13, 7, 0, -1, EnemyKind::Octopus}, {}}
    },
    // 3. LAVA (vermelho/laranja): piso de lava, 2 chamas inimigas bloqueaveis
    {
        {
            "#######D#######",
            "#~~~.......~~~#",
            "#~~~.......~~~#",
            "#~~~.......~~~#",
            "#.....~~~.....#",
            "#.....~~~.....#",
            "#~~~.......~~~#",
            "#~~~.......~~~#",
            "#~~~.......~~~#",
            "###############"
        },
        {2, 5}, {12, 5}, {7, 1},
        true, {10, 7},
        false, false,
        3, {{4, 4}, {4, 5}, {9, 3}, {0, 0}, {0, 0}, {0, 0}},
        0, {{0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}},
        2, {{7, 2}, {7, 7}, {0, 0}, {0, 0}},
        2, {{5, 2, 1, 0, EnemyKind::Flame}, {9, 6, -1, 0, EnemyKind::Flame}, {}}
    },
    // 4. GELO (azul claro): blocos de gelo deslizantes e bolas de espinho azuis
    {
        {
            "#######D#######",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "#.............#",
            "###############"
        },
        {2, 5}, {12, 5}, {7, 1},
        true, {12, 2},
        true, false,
        4, {{4, 2}, {10, 2}, {4, 7}, {10, 7}, {0, 0}, {0, 0}},
        2, {{7, 4}, {7, 6}, {0, 0}, {0, 0}, {0, 0}, {0, 0}},
        2, {{7, 5}, {2, 2}, {0, 0}, {0, 0}},
        2, {{5, 3, 1, 0, EnemyKind::Spiky}, {9, 7, -1, 0, EnemyKind::Spiky}, {}}
    }
};

} // namespace sokoban

#endif
