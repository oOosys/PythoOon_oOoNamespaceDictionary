-- SciTE pastLexer Code Highlighting using  Indicator Configuration
-- Lua Code created running:  SciTEStartupLuaCodeFor_PythoOon_pastLexerCodeHighlighting.py 

-- Search flags
SCFIND_NONE = 0
SCFIND_REGEXP = 0x00200000

-- Define patterns and their indicators
local patterns = {
    {text = "o['", indicator = 0, searchFlag = 0},
    {text = "']", indicator = 0, searchFlag = 0},
    {text = "o-@", indicator = 0, searchFlag = 0},
    {text = "@-o", indicator = 0, searchFlag = 0},
    {text = "o@-", indicator = 0, searchFlag = 0},
    {text = "-@o", indicator = 0, searchFlag = 0},
    {text = "o@~", indicator = 0, searchFlag = 0},
    {text = "~@o", indicator = 0, searchFlag = 0},
    {text = "o~$", indicator = 0, searchFlag = 0},
    {text = "$~o", indicator = 0, searchFlag = 0},
}
-- Function to highlight all patterns
function pastLexerStyleOf_oOoNamespaceMarkerPatterns()
	-- Configure indicators (needs to be done here as editor.* unavailable at Lua start)
	if editor.IndicStyle[0] ~= INDIC_TEXTFORE then
		-- Indicator 0: INDIC_TEXTFORE
		editor.IndicStyle[0] = INDIC_TEXTFORE
		editor.IndicFore[0] = 0xE9FDE9
	end
	
	-- Apply each pattern
	for _, pattern in ipairs(patterns) do
		editor.IndicatorCurrent = pattern.indicator
		editor.SearchFlags = pattern.searchFlag
		editor.TargetStart = 0
		editor.TargetEnd = editor.Length
		
		while editor:SearchInTarget(pattern.text) ~= -1 do
			editor:IndicatorFillRange(editor.TargetStart, editor.TargetEnd - editor.TargetStart)
			editor.TargetStart = editor.TargetEnd
			editor.TargetEnd = editor.Length
		end
	end
end

-- Hook into document events
function OnSave(filename)
	pastLexerStyleOf_oOoNamespaceMarkerPatterns()
end
