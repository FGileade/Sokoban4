-- QA automatizado no mGBA para Sokoban4-main
local frame = 0
local crashed = false

callbacks:add("crashed", function()
    crashed = true
    console:log("[QA FALHA] Crash detectado no frame " .. tostring(frame))
end)

callbacks:add("frame", function()
    frame = frame + 1

    if frame == 25 then
        emu:screenshot("qa_c1_pantano.png")
    elseif frame == 40 then
        emu:addKey(C.GBA_KEY.RIGHT)
    elseif frame == 55 then
        emu:clearKeys(0x3FF)
        emu:addKey(C.GBA_KEY.R)
    elseif frame == 85 then
        emu:clearKeys(0x3FF)
        emu:addKey(C.GBA_KEY.L)
    elseif frame == 135 then
        emu:clearKeys(0x3FF)
        emu:screenshot("qa_c2_agua.png")
        emu:addKey(C.GBA_KEY.L)
    elseif frame == 185 then
        emu:clearKeys(0x3FF)
        emu:screenshot("qa_c3_lava.png")
        emu:addKey(C.GBA_KEY.L)
    elseif frame == 235 then
        emu:clearKeys(0x3FF)
        emu:screenshot("qa_c4_gelo.png")
        if not crashed then
            console:log("[QA OK] 4 camaras e reset testados sem crash (235 frames).")
        end
    end
end)
