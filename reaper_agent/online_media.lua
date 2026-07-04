-- fuerza toda la media online (tras regenerar twisted_nerve.wav)
reaper.Main_OnCommand(40101, 0)  -- Item: Set all media online
reaper.UpdateArrange()
reaper.ShowConsoleMsg("media online OK\n")
