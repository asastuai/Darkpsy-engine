--[[
   ARRANGE WHISTLE MOMENT  (ReaScript Lua)
   Consigna de Juan: el silbido (CINE) suena SOLO hasta 0:21, y en ese instante
   entra la base TAL CUAL desde su primer kick. Corre sobre el proyecto abierto.

   Cómo correrlo en Reaper:
     Actions  ->  Show action list  ->  "New action..." -> "Load ReaScript..."
     -> elegí este archivo -> queda en la lista -> Run (o doble-clic).
   (Se puede deshacer con Ctrl+Z: hace todo en un solo Undo.)
]]--

local DROP    = 21.0      -- el silbido suena solo hasta acá; acá entra la base
local KICKOFF = 18.183    -- primer kick del stem -> queda alineado al segundo 21

reaper.Undo_BeginBlock()
local proj = 0

local function take_src_name(it)
  local tk = reaper.GetActiveTake(it)
  if not tk then return "" end
  local src = reaper.GetMediaItemTake_Source(tk)
  local fn = reaper.GetMediaSourceFileName(src, "")
  return (fn or ""):lower()
end

local function is_whistle(tr)
  local _, name = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false)
  if name and name:upper():find("CINE") then return true end
  local nit = reaper.CountTrackMediaItems(tr)
  for i = 0, nit - 1 do
    if take_src_name(reaper.GetTrackMediaItem(tr, i)):find("twisted_nerve") then
      return true
    end
  end
  return false
end

-- guarda: si no hay silbido en el proyecto, no tocamos nada
local ntr = reaper.CountTracks(proj)
local has_whistle = false
for t = 0, ntr - 1 do
  if is_whistle(reaper.GetTrack(proj, t)) then has_whistle = true break end
end
if not has_whistle then
  reaper.Undo_EndBlock("Arrange whistle moment (abortado)", -1)
  reaper.ShowMessageBox(
    "No encontré el silbido en este proyecto.\n\nAbrí ULTIMOREAPER_cine.RPP, o arrastrá\ntwisted_nerve.wav a una pista, y volvé a correr.",
    "Whistle moment", 0)
  return
end

local moved, whistled = 0, 0
for t = 0, ntr - 1 do
  local tr = reaper.GetTrack(proj, t)
  local nit = reaper.CountTrackMediaItems(tr)
  if is_whistle(tr) then
    for i = 0, nit - 1 do
      local it = reaper.GetTrackMediaItem(tr, i)
      reaper.SetMediaItemInfo_Value(it, "D_POSITION", 0)          -- arranca en 0
      reaper.SetMediaItemInfo_Value(it, "D_LENGTH", DROP)          -- suena hasta 0:21
      reaper.SetMediaItemInfo_Value(it, "D_FADEOUTLEN", 0.40)      -- fade al entrar el drop
      local tk = reaper.GetActiveTake(it)
      if tk then reaper.SetMediaItemTakeInfo_Value(tk, "D_STARTOFFS", 0) end
      whistled = whistled + 1
    end
  else
    for i = 0, nit - 1 do
      local it = reaper.GetTrackMediaItem(tr, i)
      reaper.SetMediaItemInfo_Value(it, "D_POSITION", DROP)        -- la base entra en 0:21
      local tk = reaper.GetActiveTake(it)
      if tk then reaper.SetMediaItemTakeInfo_Value(tk, "D_STARTOFFS", KICKOFF) end  -- desde el primer kick
      moved = moved + 1
    end
  end
end

reaper.UpdateArrange()
reaper.Undo_EndBlock("Arrange whistle moment (silbido solo -> 0:21 -> drop)", -1)
reaper.ShowMessageBox(
  "Listo.\n\nSilbido solo hasta 0:" .. math.floor(DROP) ..
  "\nLa base entra en 0:" .. math.floor(DROP) .. " desde el primer kick (" .. KICKOFF .. "s)" ..
  "\n\nItems de base movidos: " .. moved .. "   |   silbido: " .. whistled ..
  "\n\n(Ctrl+Z para deshacer)", "Whistle moment", 0)
