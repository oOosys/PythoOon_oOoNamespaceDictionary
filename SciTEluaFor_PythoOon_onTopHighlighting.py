#!/usr/local/bin/python3.15
#						oOosys ( Claude Sonnet 4.5 )				     2025-11-24_10:14
#													lastUpdate :	     2025-11-29_18:30
''' oOoMage helper asking user for custom keywords and their highlighting style in order 
	to provide Lua code for copy/paste to  ~/.SciTEstartup.lua  . The effect of this code
	    is usage of Scintilla Indicator feature for pastLexer custom keywords highlighting. '''
# ---
OAppOtitle	= "PythoOon: .SciTEStartup.lua for onTopHighlghting of oOoNamespace syntax."
OAppOgeom = ( 100, 100, 1300, 800 )
previewBackgroundColorHex	= "#2b2b2b"
maximumIndicatorsAmount		=  16
defaultTransparencyValue		=  255
defaultTextUnderValue			= bool("Yes")
# ---
## Disabling of : 
# qt.accessibility.atspi: Received text event for invalid interface.
# qt.accessibility.atspi: Could not find accessible on path: "/org/a11y/atspi/accessible/2147483694"
import os
os.environ['QT_LINUX_ACCESSIBILITY_ALWAYS_ON'] = '0'
os.environ['NO_AT_BRIDGE'] = '1'
os.environ['QT_LOGGING_RULES'] = 'qt.accessibility*=false'
'''The trick --^-- here is to use all three environment variables together:				
		os.environ['QT_LINUX_ACCESSIBILITY_ALWAYS_ON'] = '0'					
		os.environ['NO_AT_BRIDGE'] = '1'											
		os.environ['QT_LOGGING_RULES'] = 'qt.accessibility*=false'					
	Each one tackles a different part of the accessibility stack:						
		NO_AT_BRIDGE prevents loading the AT-SPI bridge library					
		QT_LINUX_ACCESSIBILITY_ALWAYS_ON=0  refrain from forcing accessibility	
		QT_LOGGING_RULES suppresses any remaining accessibility log messages       '''

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
	QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, 
	QCheckBox, QTextEdit, QScrollArea, QFrame, QColorDialog, QFileDialog,
	QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from pprint import pformat
import sys

# SciTE search flags
SCFIND_NONE = 0
SCFIND_REGEXP = 0x00200000

IndicatorStylesWithDescriptions = {
	"INDIC_PLAIN"					: "Plain underline"			,
	"INDIC_SQUIGGLE"			: "Squiggly underline"		,
	"INDIC_TT"						: "TT underline"			,
	"INDIC_DIAGONAL"			: "Diagonal hatching"		,
	"INDIC_STRIKE"				: "Strike-out"				,
	"INDIC_HIDDEN"				: "Hidden"					,
	"INDIC_BOX"					: "Box"						,
	"INDIC_ROUNDBOX"			: "Rounded box"			,
	"INDIC_STRAIGHTBOX"		: "Straight box"			,
	"INDIC_FULLBOX"				: "Full box"					,
	"INDIC_DASH"					: "Dashed underline"		,
	"INDIC_DOTS"					: "Dotted underline"		,
	"INDIC_SQUIGGLELOW"		: "Squiggle low"			,
	"INDIC_DOTBOX"				: "Dotted box"				,
	"INDIC_TEXTFORE"			: "Text foreground color"	,
	"INDIC_POINT"					: "Point"					,
	"INDIC_POINTCHARACTER"	: "Point character"			,
}
IndicatorDescriptionsToConstants = {desc: const for const, desc in IndicatorStylesWithDescriptions.items()}

StylesUsingForegroundColor = {
	"INDIC_TEXTFORE",
	"INDIC_PLAIN",
	"INDIC_SQUIGGLE",
	"INDIC_TT",
	"INDIC_DIAGONAL",
	"INDIC_STRIKE",
	"INDIC_DASH",
	"INDIC_DOTS",
	"INDIC_SQUIGGLELOW",
	"INDIC_POINT",
	"INDIC_POINTCHARACTER",
}

StylesUsingBackgroundColor = {
	"INDIC_BOX",
	"INDIC_ROUNDBOX",
	"INDIC_STRAIGHTBOX",
	"INDIC_FULLBOX",
	"INDIC_DOTBOX",
	"INDIC_DIAGONAL",
	"INDIC_HIDDEN",
}

StylesNeedingAlphaAndUnder = {
	"INDIC_BOX",
	"INDIC_ROUNDBOX",
	"INDIC_STRAIGHTBOX",
	"INDIC_FULLBOX",
	"INDIC_DOTBOX",
}

StylesBeingBoxes = StylesNeedingAlphaAndUnder

# Global state
KeywordsWithConfigurations	= []
nextIndicatorId					= 0
KeywordFramesInScrollArea		= []
ColorPalette					= []
selectedKeywordIndex			= None

def oOO_customColorPaletteAsQColorsList_OOo_fromKeywords_oO_KeywordsWithConfigurations_Oo(KeywordsWithConfigurations=None):
	"""Build custom color palette from existing keyword colors"""
	if KeywordsWithConfigurations is None:
		KeywordsWithConfigurations = globals()['KeywordsWithConfigurations']
	
	UniqueColorsAsHexSet = set()
	for keywordConfig in KeywordsWithConfigurations:
		fgColorHex = keywordConfig.get('fgColorHex')
		if fgColorHex is not None:
			UniqueColorsAsHexSet.add(fgColorHex)
		
		bgColorHex = keywordConfig.get('bgColorHex')
		if bgColorHex is not None:
			UniqueColorsAsHexSet.add(bgColorHex)
	
	CustomColorsList = [QColor(colorHex) for colorHex in sorted(UniqueColorsAsHexSet)]
	
	customColorsListTooShort = len(CustomColorsList) < 16
	if customColorsListTooShort:
		CustomColorsList = CustomColorsList + [QColor(255, 255, 255)] * (16 - len(CustomColorsList))
	else:
		CustomColorsList = CustomColorsList[:16]
	
	return CustomColorsList

def oOO_colorHexFromDialog_OOo_withInitial_oO_initialColorHex_Oo(initialColorHex=None):
	"""Show color picker dialog with custom palette from configuration colors"""
	if initialColorHex is None:
		initialColorHex = "#888888"
	
	CustomColorsList = oOO_customColorPaletteAsQColorsList_OOo_fromKeywords_oO_KeywordsWithConfigurations_Oo()
	
	for paletteIndex, qColor in enumerate(CustomColorsList):
		QColorDialog.setCustomColor(paletteIndex, qColor)
	
	colorDialog = QColorDialog()
	colorDialog.setWindowTitle("oOo Select Color")
	colorDialog.setCurrentColor(QColor(initialColorHex))
	colorDialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
	
	dialogWasAccepted = colorDialog.exec()
	if dialogWasAccepted:
		selectedQColor = colorDialog.selectedColor()
		colorHexFromDialog = selectedQColor.name()
		return colorHexFromDialog
	
	return initialColorHex

def oOO_stylesListForSecondCombo_OOo_basedOn_oO_firstStyleSelection_Oo(firstStyleSelection=None):
	"""Return compatible styles for second combo based on first selection"""
	if firstStyleSelection is None:
		return ["(none)"]
	
	firstStyleConstant = IndicatorDescriptionsToConstants.get(firstStyleSelection, firstStyleSelection)
	
	firstStyleUsesForeground = firstStyleConstant in StylesUsingForegroundColor
	if firstStyleUsesForeground:
		compatibleStyleConstants = [s for s in StylesUsingBackgroundColor if s != firstStyleConstant]
	else:
		compatibleStyleConstants = [s for s in StylesUsingForegroundColor if s != firstStyleConstant]
	
	compatibleStyleDescriptions = ["(none)"] + [IndicatorStylesWithDescriptions[const] for const in sorted(compatibleStyleConstants)]
	
	return compatibleStyleDescriptions

def oOO_applicationState_OOo_nowWithUpdatedSecondStyleCombo():
	"""Update second style combo based on first style selection"""
	firstStyleSelection = style1ComboBox.currentText()
	compatibleStyles = oOO_stylesListForSecondCombo_OOo_basedOn_oO_firstStyleSelection_Oo(firstStyleSelection)
	
	currentSecondStyle = style2ComboBox.currentText()
	style2ComboBox.clear()
	style2ComboBox.addItems(compatibleStyles)
	
	secondStyleStillValid = currentSecondStyle in compatibleStyles
	if secondStyleStillValid:
		style2ComboBox.setCurrentText(currentSecondStyle)
	else:
		style2ComboBox.setCurrentText("(none)")

def oOO_applicationState_OOo_nowWithUpdatedColorFieldStates():
	"""Update color field states based on selected styles"""
	style1Description = style1ComboBox.currentText()
	style2Description = style2ComboBox.currentText()
	
	style1Constant = IndicatorDescriptionsToConstants.get(style1Description, "")
	style2Constant = IndicatorDescriptionsToConstants.get(style2Description, "")
	
	style1UsesForeground = style1Constant in StylesUsingForegroundColor
	style2UsesForeground = style2Constant in StylesUsingForegroundColor
	style2IsActive = style2Description != "(none)"
	
	if style2IsActive:
		fgColorInput.setEnabled(True)
		fgColorButton.setEnabled(True)
		bgColorInput.setEnabled(True)
		bgColorButton.setEnabled(True)
		
		fgColorInput.setStyleSheet(f"background-color: {fgColorInput.text()}; color: white;")
		bgColorInput.setStyleSheet(f"background-color: {bgColorInput.text()}; color: black;")
	else:
		if style1UsesForeground:
			fgColorInput.setEnabled(True)
			fgColorButton.setEnabled(True)
			fgColorInput.setStyleSheet(f"background-color: {fgColorInput.text()}; color: white;")
			
			bgColorInput.setEnabled(False)
			bgColorButton.setEnabled(False)
			bgColorInput.setStyleSheet("background-color: #cccccc;")
		else:
			bgColorInput.setEnabled(True)
			bgColorButton.setEnabled(True)
			bgColorInput.setStyleSheet(f"background-color: {bgColorInput.text()}; color: black;")
			
			fgColorInput.setEnabled(False)
			fgColorButton.setEnabled(False)
			fgColorInput.setStyleSheet("background-color: #cccccc;")
	
	anyStyleIsBox = style1Constant in StylesBeingBoxes or (style2IsActive and style2Constant in StylesBeingBoxes)
	alphaSpinBox.setEnabled(anyStyleIsBox)
	underCheckBox.setEnabled(anyStyleIsBox)

def oOO_bgrHexForScite_OOo_fromRgbHex_oO_rgbColorHex_Oo(rgbColorHex=None):
	"""Convert #RRGGBB to 0xBBGGRR for SciTE"""
	if rgbColorHex is None:
		rgbColorHex = rgbColorHex
	rgbColorHex = rgbColorHex.lstrip('#')
	redValue = int(rgbColorHex[0:2], 16)
	greenValue = int(rgbColorHex[2:4], 16)
	blueValue = int(rgbColorHex[4:6], 16)
	bgrHexForScite = f"0x{blueValue:02X}{greenValue:02X}{redValue:02X}"
	return bgrHexForScite

def oOO_luaCodeForSciteStartup_OOo_fromKeywords_oO_KeywordsWithConfigurations_Oo(KeywordsWithConfigurations=None):
	"""Generate complete Lua startup script"""
	if KeywordsWithConfigurations is None:
		KeywordsWithConfigurations = globals()['KeywordsWithConfigurations']
	
	luaCode = f"""-- SciTE pastLexer Code Highlighting using  Indicator Configuration
-- Lua Code created running:  { __file__[ __file__.rfind('/') +1 : ] } 

-- Search flags
SCFIND_NONE = 0
SCFIND_REGEXP = 0x00200000

-- Define patterns and their indicators
local patterns = {{
"""
	
	for keywordConfig in KeywordsWithConfigurations:
		for indicatorId in keywordConfig['indicatorIds']:
			searchFlag = keywordConfig.get('searchFlag', 0)
			luaCode += f'    {{text = "{keywordConfig['keyword']}", indicator = {indicatorId}, searchFlag = {searchFlag}}},\n'
	
	luaCode += "}\n"
	
	UniqueIndicatorConfigs = {}
	for keywordConfig in KeywordsWithConfigurations:
		for idx, indicatorId in enumerate(keywordConfig['indicatorIds']):
			if indicatorId not in UniqueIndicatorConfigs:
				styleForIndicator = keywordConfig['styles'][idx]
				UniqueIndicatorConfigs[indicatorId] = {'style': styleForIndicator}
				
				if styleForIndicator in StylesUsingForegroundColor:
					UniqueIndicatorConfigs[indicatorId]['fgColor'] = keywordConfig.get('fgColor')
				
				if styleForIndicator in StylesUsingBackgroundColor:
					UniqueIndicatorConfigs[indicatorId]['bgColor'] = keywordConfig.get('bgColor')
				
				if styleForIndicator in StylesNeedingAlphaAndUnder:
					UniqueIndicatorConfigs[indicatorId]['alpha'] = keywordConfig.get('alpha', defaultTransparencyValue)
					UniqueIndicatorConfigs[indicatorId]['under'] = keywordConfig.get('under', defaultTextUnderValue)
	
	luaCode += """-- Function to highlight all patterns
function pastLexerStyleOf_oOoNamespaceMarkerPatterns()
	-- Configure indicators (needs to be done here as editor.* unavailable at Lua start)
"""
	
	if UniqueIndicatorConfigs:
		firstStyle = list(UniqueIndicatorConfigs.values())[0]['style']
		luaCode += f"\tif editor.IndicStyle[0] ~= {firstStyle} then\n"
		
		for indicatorId in sorted(UniqueIndicatorConfigs.keys()):
			config = UniqueIndicatorConfigs[indicatorId]
			luaCode += f"\t\t-- Indicator {indicatorId}: {config['style']}\n"
			luaCode += f"\t\teditor.IndicStyle[{indicatorId}] = {config['style']}\n"
			
			styleUsesForeground = config['style'] in StylesUsingForegroundColor
			if styleUsesForeground:
				colorToUse = config.get('fgColor')
			else:
				colorToUse = config.get('bgColor')
			
			if colorToUse is not None:
				luaCode += f"\t\teditor.IndicFore[{indicatorId}] = {colorToUse}\n"
			
			styleNeedsAlphaAndUnder = config['style'] in StylesNeedingAlphaAndUnder
			if styleNeedsAlphaAndUnder:
				alphaValue = config.get('alpha', defaultTransparencyValue)
				underValue = config.get('under', defaultTextUnderValue)
				luaCode += f"\t\teditor.IndicAlpha[{indicatorId}] = {alphaValue}\n"
				underValueAsString = str(underValue).lower()
				luaCode += f"\t\teditor.IndicUnder[{indicatorId}] = {underValueAsString}\n"
		
		luaCode += "\tend\n"
	
	luaCode += """	
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
"""
	return luaCode

def oOO_indicatorIdForStyle_OOo_matching_oO_style_Oo_oO_fgColorHex_Oo_oO_bgColorHex_Oo_oO_alpha_Oo_oO_under_Oo(style=None, fgColorHex=None, bgColorHex=None, alpha=None, under=None):
	"""Find existing indicator with matching style or return None"""
	if style is None:
		return None
	
	styleUsesForeground = style in StylesUsingForegroundColor
	styleUsesBackground = style in StylesUsingBackgroundColor
	styleNeedsAlphaAndUnder = style in StylesNeedingAlphaAndUnder
	
	for keywordConfig in KeywordsWithConfigurations:
		for idx, existingStyle in enumerate(keywordConfig['styles']):
			styleMatches = existingStyle == style
			if styleMatches:
				colorMatches = True
				
				if styleUsesForeground:
					colorMatches = colorMatches and keywordConfig.get('fgColorHex') == fgColorHex
				
				if styleUsesBackground:
					colorMatches = colorMatches and keywordConfig.get('bgColorHex') == bgColorHex
				
				if styleNeedsAlphaAndUnder:
					alphaMatches = keywordConfig.get('alpha', defaultTransparencyValue) == alpha
					underMatches = keywordConfig.get('under', defaultTextUnderValue) == under
					colorMatches = colorMatches and alphaMatches and underMatches
				
				if colorMatches:
					return keywordConfig['indicatorIds'][idx]
	
	return None

def oOOO_KeywordsWithConfigurations_OOOo_withNewKeyword_oO_keywordText_Oo_oO_style1_Oo_oO_style2_Oo_oO_fgColorHex_Oo_oO_bgColorHex_Oo_oO_alpha_Oo_oO_under_Oo_oO_isRegex_Oo():
	"""Add new keyword configuration to global list (with optional second style and regex support)"""
	global KeywordsWithConfigurations, nextIndicatorId
	
	StylesToApply = [style1]
	style2IsActive = style2 != "(none)"
	if style2IsActive:
		StylesToApply.append(style2)
	
	IndicatorIdsForKeyword = []
	
	for styleToApply in StylesToApply:
		existingIndicatorId = oOO_indicatorIdForStyle_OOo_matching_oO_style_Oo_oO_fgColorHex_Oo_oO_bgColorHex_Oo_oO_alpha_Oo_oO_under_Oo(
			styleToApply, fgColorHex, bgColorHex, alpha, under
		)
		
		styleAlreadyExists = existingIndicatorId is not None
		if styleAlreadyExists:
			indicatorIdToUse = existingIndicatorId
		else:
			maximumIndicatorsReached = nextIndicatorId >= maximumIndicatorsAmount
			if maximumIndicatorsReached:
				return False
			indicatorIdToUse = nextIndicatorId
			nextIndicatorId += 1
		
		IndicatorIdsForKeyword.append(indicatorIdToUse)
	
	searchFlag = SCFIND_REGEXP if isRegex else SCFIND_NONE
	
	newKeywordConfig = {
		'keyword': keywordText,
		'indicatorIds': IndicatorIdsForKeyword,
		'styles': StylesToApply,
		'isRegex': isRegex,
		'searchFlag': searchFlag
	}
	
	anyStyleUsesForeground = any(style in StylesUsingForegroundColor for style in StylesToApply)
	anyStyleUsesBackground = any(style in StylesUsingBackgroundColor for style in StylesToApply)
	anyStyleNeedsAlphaAndUnder = any(style in StylesNeedingAlphaAndUnder for style in StylesToApply)
	
	if anyStyleUsesForeground:
		fgColorForScite = oOO_bgrHexForScite_OOo_fromRgbHex_oO_rgbColorHex_Oo(fgColorHex)
		newKeywordConfig['fgColor'] = fgColorForScite
		newKeywordConfig['fgColorHex'] = fgColorHex
	
	if anyStyleUsesBackground:
		bgColorForScite = oOO_bgrHexForScite_OOo_fromRgbHex_oO_rgbColorHex_Oo(bgColorHex)
		newKeywordConfig['bgColor'] = bgColorForScite
		newKeywordConfig['bgColorHex'] = bgColorHex
	
	if anyStyleNeedsAlphaAndUnder:
		newKeywordConfig['alpha'] = alpha
		newKeywordConfig['under'] = under
	
	KeywordsWithConfigurations.append(newKeywordConfig)
	print(f"{newKeywordConfig=}")

	return True

def oOOO_KeywordFramesInScrollArea_OOOo_withVisualRepresentation_oO_keywordConfig_Oo(localKeywordConfig=None):
	"""Create visual representation of keyword in scroll area"""
	global KeywordFramesInScrollArea
	if localKeywordConfig:
		keywordConfig = localKeywordConfig
	
	keywordFrame = QFrame()
	keywordFrameLayout = QHBoxLayout()
	keywordFrame.setLayout(keywordFrameLayout)
	keywordFrame.setFrameStyle(QFrame.Shape.Box)
	keywordFrame.setStyleSheet("QFrame { background-color: transparent; }")
	keywordFrame.setCursor(Qt.CursorShape.PointingHandCursor)
	
	hasTwoStyles = len(keywordConfig['styles']) == 2
	if hasTwoStyles:
		displayBackgroundColorHex = keywordConfig.get('bgColorHex', previewBackgroundColorHex)
		displayForegroundColorHex = keywordConfig.get('fgColorHex', '#FFFFFF')
	else:
		singleStyle = keywordConfig['styles'][0]
		styleUsesForeground = singleStyle in StylesUsingForegroundColor
		if styleUsesForeground:
			displayBackgroundColorHex = previewBackgroundColorHex
			displayForegroundColorHex = keywordConfig.get('fgColorHex', '#888888')
		else:
			displayBackgroundColorHex = keywordConfig.get('bgColorHex', '#FFFF00')
			displayForegroundColorHex = "#000000"
	
	keywordTextEscaped = keywordConfig['keyword'].replace('<', '&lt;').replace('>', '&gt;')
	
	isRegex = keywordConfig.get('isRegex', False)
	regexIndicator = " [REGEX]" if isRegex else ""
	
	styledHtml = f'<span style="background-color: {displayBackgroundColorHex}; color: {displayForegroundColorHex}; padding: 5px; border: 1px solid #555;">{keywordTextEscaped}{regexIndicator}</span>'
	
	previewLabel = QLabel()
	previewLabel.setTextFormat(Qt.TextFormat.RichText)
	previewLabel.setText(styledHtml)
	previewLabel.setMinimumWidth(150)
	previewLabel.setStyleSheet("padding: 5px;")
	previewLabel.setCursor(Qt.CursorShape.PointingHandCursor)
	
	stylesText = " + ".join([IndicatorStylesWithDescriptions[s] for s in keywordConfig['styles']])
	indicatorIdsText = ",".join([str(id) for id in keywordConfig['indicatorIds']])
	
	hasBoxStyle = any(s in StylesBeingBoxes for s in keywordConfig['styles'])
	extraInfo = ""
	if hasBoxStyle:
		alphaValue = keywordConfig.get('alpha', defaultTransparencyValue)
		underValue = keywordConfig.get('under', defaultTextUnderValue)
		underText = "under" if underValue else "over"
		alphaPercent = int((alphaValue / 255) * 100)
		extraInfo = f" | Alpha: {alphaValue} ({alphaPercent}%) | {underText} text"

	infoText = f"IDs: {indicatorIdsText} | {stylesText}{extraInfo}"
	infoLabel = QLabel(infoText)
	infoLabel.setCursor(Qt.CursorShape.PointingHandCursor)
	
	keywordFrameIndex = len(KeywordFramesInScrollArea)
	
	previewLabel.mousePressEvent = lambda event: oOO_applicationState_OOo_nowWithSelectedKeyword_oO_keywordIndex_Oo(keywordFrameIndex)
	infoLabel.mousePressEvent = lambda event: oOO_applicationState_OOo_nowWithSelectedKeyword_oO_keywordIndex_Oo(keywordFrameIndex)
	keywordFrame.mousePressEvent = lambda event: oOO_applicationState_OOo_nowWithSelectedKeyword_oO_keywordIndex_Oo(keywordFrameIndex)
	
	removeButton = QPushButton("Remove")
	removeButton.clicked.connect(lambda: oOOO_KeywordFramesInScrollArea_OOOo_withoutFrame_oO_frameIndex_Oo(keywordFrameIndex))
	
	keywordFrameLayout.addWidget(previewLabel)
	keywordFrameLayout.addWidget(infoLabel)
	keywordFrameLayout.addStretch()
	keywordFrameLayout.addWidget(removeButton)
	
	keywordsScrollAreaLayout.addWidget(keywordFrame)
	KeywordFramesInScrollArea.append(keywordFrame)

def oOO_applicationState_OOo_nowWithSelectedKeyword_oO_keywordIndex_Oo(keywordIndex=None):
	"""Load selected keyword data into input fields for editing"""
	global selectedKeywordIndex
	
	if keywordIndex is None or keywordIndex >= len(KeywordsWithConfigurations):
		return
	
	selectedKeywordIndex = keywordIndex
	keywordConfig = KeywordsWithConfigurations[keywordIndex]
	
	# Highlight selected frame
	for frameIndex, frame in enumerate(KeywordFramesInScrollArea):
		frameIsSelected = frameIndex == keywordIndex
		if frameIsSelected:
			frame.setStyleSheet("QFrame { background-color: #404040; }")
		else:
			frame.setStyleSheet("QFrame { background-color: transparent; }")
	
	# Load keyword text
	keywordInput.setText(keywordConfig['keyword'])
	
	# Load styles
	style1Description = IndicatorStylesWithDescriptions[keywordConfig['styles'][0]]
	style1ComboBox.setCurrentText(style1Description)
	
	hasTwoStyles = len(keywordConfig['styles']) == 2
	if hasTwoStyles:
		style2Description = IndicatorStylesWithDescriptions[keywordConfig['styles'][1]]
		style2ComboBox.setCurrentText(style2Description)
	else:
		style2ComboBox.setCurrentText("(none)")
	
	# Load colors
	fgColorHexFromConfig = keywordConfig.get('fgColorHex', '#888888')
	bgColorHexFromConfig = keywordConfig.get('bgColorHex', '#FFFF00')
	fgColorInput.setText(fgColorHexFromConfig)
	bgColorInput.setText(bgColorHexFromConfig)
	
	# Load alpha and under
	alphaFromConfig = keywordConfig.get('alpha', defaultTransparencyValue)
	underFromConfig = keywordConfig.get('under', defaultTextUnderValue)
	alphaSpinBox.setValue(alphaFromConfig)
	underCheckBox.setChecked(underFromConfig)
	
	# Load regex setting
	isRegexFromConfig = keywordConfig.get('isRegex', False)
	regexCheckBox.setChecked(isRegexFromConfig)
	
	# Update UI states
	oOO_applicationState_OOo_nowWithUpdatedSecondStyleCombo()
	oOO_applicationState_OOo_nowWithUpdatedColorFieldStates()
	
	# Update button states
	addButton.setEnabled(False)
	updateButton.setEnabled(True)
	cancelButton.setEnabled(True)

def oOO_applicationState_OOo_nowWithUpdatedKeyword():
	"""Update existing keyword with current field values"""
	global selectedKeywordIndex, nextIndicatorId
	
	selectedKeywordIndexIsNone = selectedKeywordIndex is None
	if selectedKeywordIndexIsNone:
		return
	
	keywordText = keywordInput.text().strip()
	keywordTextIsEmpty = len(keywordText) == 0
	if keywordTextIsEmpty:
		QMessageBox.warning(OAppO, "Warning", "Please enter a keyword")
		return
	
	style1Description = style1ComboBox.currentText()
	style1 = IndicatorDescriptionsToConstants[style1Description]
	
	style2Description = style2ComboBox.currentText()
	if style2Description == "(none)":
		style2 = "(none)"
	else:
		style2 = IndicatorDescriptionsToConstants[style2Description]
	
	fgColorHex = fgColorInput.text()
	bgColorHex = bgColorInput.text()
	alpha = alphaSpinBox.value()
	under = underCheckBox.isChecked()
	isRegex = regexCheckBox.isChecked()
	
	# Build updated keyword configuration
	StylesToApply = [style1]
	style2IsActive = style2 != "(none)"
	if style2IsActive:
		StylesToApply.append(style2)
	
	searchFlag = SCFIND_REGEXP if isRegex else SCFIND_NONE
	
	newKeywordConfig = {
		'keyword': keywordText,
		'indicatorIds': [],
		'styles': StylesToApply,
		'isRegex': isRegex,
		'searchFlag': searchFlag
	}
	# Find or assign indicator IDs
	IndicatorIdsForKeyword = []
	for idx, styleToApply in enumerate(StylesToApply):
		existingIndicatorId = oOO_indicatorIdForStyle_OOo_matching_oO_style_Oo_oO_fgColorHex_Oo_oO_bgColorHex_Oo_oO_alpha_Oo_oO_under_Oo(
			styleToApply, fgColorHex, bgColorHex, alpha, under
		)
		
		if existingIndicatorId is not None:
			IndicatorIdsForKeyword.append(existingIndicatorId)
		else:
			IndicatorIdsForKeyword.append(nextIndicatorId)
			nextIndicatorId += 1
	
	newKeywordConfig['indicatorIds'] = IndicatorIdsForKeyword
	
	anyStyleUsesForeground = any(style in StylesUsingForegroundColor for style in StylesToApply)
	anyStyleUsesBackground = any(style in StylesUsingBackgroundColor for style in StylesToApply)
	anyStyleNeedsAlphaAndUnder = any(style in StylesNeedingAlphaAndUnder for style in StylesToApply)
	
	if anyStyleUsesForeground:
		fgColorForScite = oOO_bgrHexForScite_OOo_fromRgbHex_oO_rgbColorHex_Oo(fgColorHex)
		newKeywordConfig['fgColor'] = fgColorForScite
		newKeywordConfig['fgColorHex'] = fgColorHex
	
	if anyStyleUsesBackground:
		bgColorForScite = oOO_bgrHexForScite_OOo_fromRgbHex_oO_rgbColorHex_Oo(bgColorHex)
		newKeywordConfig['bgColor'] = bgColorForScite
		newKeywordConfig['bgColorHex'] = bgColorHex
	
	if anyStyleNeedsAlphaAndUnder:
		newKeywordConfig['alpha'] = alpha
		newKeywordConfig['under'] = under
	
	# Replace old configuration
	KeywordsWithConfigurations[selectedKeywordIndex] = newKeywordConfig
	
	# Rebuild indicator IDs for all keywords
	nextIndicatorId = 0
	for keywordConfig in KeywordsWithConfigurations:
		newIndicatorIds = []
		for _ in keywordConfig['indicatorIds']:
			newIndicatorIds.append(nextIndicatorId)
			nextIndicatorId += 1
		keywordConfig['indicatorIds'] = newIndicatorIds
	
	# Rebuild visual list
	oOOO_KeywordFramesInScrollArea_OOOo_rebuiltFromConfigurations()
	
	# Clear selection
	oOO_applicationState_OOo_nowWithClearedSelection()

def oOO_applicationState_OOo_nowWithClearedSelection():
	"""Clear keyword selection and reset input fields"""
	global selectedKeywordIndex
	selectedKeywordIndex = None
	# Clear highlight from all frames
	for frame in KeywordFramesInScrollArea:
		frame.setStyleSheet("QFrame { background-color: transparent; }")
	
	# Clear input fields
	keywordInput.clear()
	style1ComboBox.setCurrentText("Text foreground color")
	style2ComboBox.setCurrentText("(none)")
	fgColorInput.setText("#888888")
	bgColorInput.setText("#FFFF00")
	alphaSpinBox.setValue(60)
	underCheckBox.setChecked(True)
	regexCheckBox.setChecked(False)
	
	# Update button states
	addButton.setEnabled(True)
	updateButton.setEnabled(False)
	cancelButton.setEnabled(False)
	
	oOO_applicationState_OOo_nowWithUpdatedColorFieldStates()

def oOOO_KeywordFramesInScrollArea_OOOo_withoutFrame_oO_frameIndex_Oo(frameIndex=None):
	"""Remove keyword frame and rebuild configuration"""
	global KeywordFramesInScrollArea, KeywordsWithConfigurations, nextIndicatorId, selectedKeywordIndex
	if frameIndex is None:
		return
	
	# Clear selection if removed item was selected
	frameIndexWasSelected = selectedKeywordIndex == frameIndex
	if frameIndexWasSelected:
		selectedKeywordIndex = None
	
	frameToRemove = KeywordFramesInScrollArea[frameIndex]
	frameToRemove.deleteLater()
	KeywordFramesInScrollArea.pop(frameIndex)
	KeywordsWithConfigurations.pop(frameIndex)
	
	# Rebuild indicator IDs
	nextIndicatorId = 0
	for keywordConfig in KeywordsWithConfigurations:
		newIndicatorIds = []
		for _ in keywordConfig['indicatorIds']:
			newIndicatorIds.append(nextIndicatorId)
			nextIndicatorId += 1
		keywordConfig['indicatorIds'] = newIndicatorIds
	oOOO_KeywordFramesInScrollArea_OOOo_rebuiltFromConfigurations()

	# Clear selection UI if needed
	if frameIndexWasSelected:
		oOO_applicationState_OOo_nowWithClearedSelection()

def oOOO_KeywordFramesInScrollArea_OOOo_rebuiltFromConfigurations():
	"""Rebuild visual keyword list from current configurations"""
	global KeywordFramesInScrollArea
	for frame in KeywordFramesInScrollArea:
		frame.deleteLater()
	KeywordFramesInScrollArea = []
	
	for keywordConfig in KeywordsWithConfigurations:
		oOOO_KeywordFramesInScrollArea_OOOo_withVisualRepresentation_oO_keywordConfig_Oo(keywordConfig)

def oOO_applicationState_OOo_nowWithAddedKeyword():
	"""Add keyword from input fields to configuration"""
	global keywordText, style1, style2, fgColorHex, bgColorHex, alpha, under, isRegex
	keywordText = keywordInput.text().strip()
	keywordTextIsEmpty = len(keywordText) == 0
	if keywordTextIsEmpty:
		QMessageBox.warning(OAppO, "Warning", "Please enter a keyword")
		return
	
	style1Description = style1ComboBox.currentText()
	style1 = IndicatorDescriptionsToConstants[style1Description]
	
	style2Description = style2ComboBox.currentText()
	if style2Description == "(none)":
		style2 = "(none)"
	else:
		style2 = IndicatorDescriptionsToConstants[style2Description]
	
	fgColorHex = fgColorInput.text()
	bgColorHex = bgColorInput.text()
	alpha = alphaSpinBox.value()
	under = underCheckBox.isChecked()
	isRegex = regexCheckBox.isChecked()
	
	keywordWasAdded = oOOO_KeywordsWithConfigurations_OOOo_withNewKeyword_oO_keywordText_Oo_oO_style1_Oo_oO_style2_Oo_oO_fgColorHex_Oo_oO_bgColorHex_Oo_oO_alpha_Oo_oO_under_Oo_oO_isRegex_Oo()
	
	if keywordWasAdded:
		lastKeywordConfig = KeywordsWithConfigurations[-1]
		oOOO_KeywordFramesInScrollArea_OOOo_withVisualRepresentation_oO_keywordConfig_Oo(lastKeywordConfig)
		keywordInput.clear()
	else:
		QMessageBox.warning(OAppO, "Warning", f"Maximum {maximumIndicatorsAmount} indicators reached")

def oOO_applicationState_OOo_nowWithForegroundColorFromDialog():
	"""Update foreground color from color picker"""
	currentFgColorHex = fgColorInput.text()
	selectedColorHex = oOO_colorHexFromDialog_OOo_withInitial_oO_initialColorHex_Oo(currentFgColorHex)
	fgColorInput.setText(selectedColorHex)
	fgColorInput.setStyleSheet(f"background-color: {selectedColorHex}; color: white;")

def oOO_applicationState_OOo_nowWithBackgroundColorFromDialog():
	"""Update background color from color picker"""
	currentBgColorHex = bgColorInput.text()
	selectedColorHex = oOO_colorHexFromDialog_OOo_withInitial_oO_initialColorHex_Oo(currentBgColorHex)
	bgColorInput.setText(selectedColorHex)
	bgColorInput.setStyleSheet(f"background-color: {selectedColorHex}; color: black;")

def oOO_applicationState_OOo_nowWithGeneratedLuaCode():
	"""Generate and display Lua code"""
	keywordsListIsEmpty = len(KeywordsWithConfigurations) == 0
	if keywordsListIsEmpty:
		QMessageBox.warning(OAppO, "Warning", "No keywords added")
		return
	luaCodeForSciteStartup = oOO_luaCodeForSciteStartup_OOo_fromKeywords_oO_KeywordsWithConfigurations_Oo()
	codeTextEdit.setPlainText(luaCodeForSciteStartup)

def oOO_clipboard_OOo_nowWithLuaCode():
	"""Copy generated code to clipboard"""
	luaCodeText = codeTextEdit.toPlainText()
	OApp.clipboard().setText(luaCodeText)
	QMessageBox.information(OAppO, "Success", "Code copied to clipboard")

def oOO_fileAtPath_OOo_nowWithLuaCode():
	"""Save generated code to file"""
	luaCodeText = codeTextEdit.toPlainText()
	filePath, _ = QFileDialog.getSaveFileName(
	OAppO,
	"Save Lua Script",
	"indicatorKeywordsDefinitionCode_forAppendingTo_.SciTEStartup.lua_o0.lua",
	"Lua files (*.lua);;All files (*.*)"
	)
	filePathWasSelected = len(filePath) > 0
	if filePathWasSelected:
		with open(filePath, 'w') as fileHandle:
			fileHandle.write(luaCodeText)
		QMessageBox.information(OAppO, "Success", f"Saved to {filePath}")

def oOO_fileAtPath_OOo_nowWithConfiguration():
	"""Save current configuration to Python dict file"""
	filePath, _ = QFileDialog.getSaveFileName(
	OAppO,
	"Save Configuration",
	"SciTEpastLexerCustomKeywordsHighlighting-oOoMaga_SessionStateBackup_o0.py",
	"Python files (*.py);;All files (*.*)"
	)
	filePathWasSelected = len(filePath) > 0
	if filePathWasSelected:
		configurationData = {	'keywords': KeywordsWithConfigurations,
								'nextIndicatorId': nextIndicatorId			}
		configurationDataAsPrettyString = pformat(configurationData, indent=1, width=100)
		with open(filePath, 'w') as fileHandle:
			fileHandle.write(f"""\
#  SciTE past-Lexer custom keyword highligting Lua code for .SciTEStartup.lua using
#  	Indicator Configuration mechanism : Mage GUI App saved session state :
ConfigurationData = {configurationDataAsPrettyString} """)
		QMessageBox.information(OAppO, "Success", f"Configuration saved to {filePath}")

def oOO_applicationState_OOo_nowWithLoadedConfiguration():
	"""Load configuration from Python dict file"""
	global KeywordsWithConfigurations, nextIndicatorId
	filePath, _ = QFileDialog.getOpenFileName(
	OAppO,
	"Load Configuration",
	"",
	"Python files (*.py);;All files (*.*)"
	)
	filePathWasSelected = len(filePath) > 0
	if filePathWasSelected:
		with open(filePath, 'r') as fileHandle:
			fileContentAsText = fileHandle.read()
		
		configurationNamespace = {}
		exec(fileContentAsText, configurationNamespace)
		configurationData = configurationNamespace['ConfigurationData']
		
		KeywordsWithConfigurations = configurationData['keywords']
		nextIndicatorId = configurationData['nextIndicatorId']
		
		for keywordConfig in KeywordsWithConfigurations:
			if 'indicatorId' in keywordConfig and 'indicatorIds' not in keywordConfig:
				keywordConfig['indicatorIds'] = [keywordConfig['indicatorId']]
				del keywordConfig['indicatorId']
			if 'style' in keywordConfig and 'styles' not in keywordConfig:
				keywordConfig['styles'] = [keywordConfig['style']]
				del keywordConfig['style']
		
		oOOO_KeywordFramesInScrollArea_OOOo_rebuiltFromConfigurations()
		QMessageBox.information(OAppO, "Success", "Configuration loaded")

# Initialize PyQt6 application
OApp = QApplication(sys.argv)
OAppO = QMainWindow()
OAppO.setWindowTitle(OAppOtitle)
OAppO.setGeometry(*OAppOgeom)
centralWidget = QWidget()
OAppO.setCentralWidget(centralWidget)

mainLayout = QVBoxLayout()
centralWidget.setLayout(mainLayout)
addKeywordGroup = QGroupBox("Add Keywords")
addKeywordLayout = QVBoxLayout()
addKeywordGroup.setLayout(addKeywordLayout)
row1Layout = QHBoxLayout()
row1Layout.addWidget(QLabel("Keyword:"))
keywordInput = QLineEdit()
row1Layout.addWidget(keywordInput)
row1Layout.addWidget(QLabel("Style 1:"))
style1ComboBox = QComboBox()
style1ComboBox.addItems(list(IndicatorStylesWithDescriptions.values()))
style1ComboBox.setCurrentText("Text foreground color")
row1Layout.addWidget(style1ComboBox)
row1Layout.addWidget(QLabel("Style 2:"))
style2ComboBox = QComboBox()
style2ComboBox.addItem("(none)")
row1Layout.addWidget(style2ComboBox)
addKeywordLayout.addLayout(row1Layout)
row2Layout = QHBoxLayout()
row2Layout.addWidget(QLabel("FG Color:"))
fgColorInput = QLineEdit("#888888")
fgColorInput.setMaximumWidth(100)
fgColorInput.setStyleSheet(f"background-color: #888888; color: white;")
row2Layout.addWidget(fgColorInput)
fgColorButton = QPushButton("Pick")
fgColorButton.clicked.connect(oOO_applicationState_OOo_nowWithForegroundColorFromDialog)
row2Layout.addWidget(fgColorButton)
row2Layout.addWidget(QLabel("BG Color:"))
bgColorInput = QLineEdit("#FFFF00")
bgColorInput.setMaximumWidth(100)
bgColorInput.setStyleSheet(f"background-color: #FFFF00; color: black;")
row2Layout.addWidget(bgColorInput)
bgColorButton = QPushButton("Pick")
bgColorButton.clicked.connect(oOO_applicationState_OOo_nowWithBackgroundColorFromDialog)
row2Layout.addWidget(bgColorButton)
addKeywordLayout.addLayout(row2Layout)
row3Layout = QHBoxLayout()
row3Layout.addWidget(QLabel("Alpha:"))
alphaSpinBox = QSpinBox()
alphaSpinBox.setRange(0, 255)
alphaSpinBox.setValue(60)
row3Layout.addWidget(alphaSpinBox)
underCheckBox = QCheckBox("Under text")
underCheckBox.setChecked(True)
row3Layout.addWidget(underCheckBox)
regexCheckBox = QCheckBox("Regex pattern")
regexCheckBox.setChecked(False)
row3Layout.addWidget(regexCheckBox)
row3Layout.addStretch()
addKeywordLayout.addLayout(row3Layout)
style1ComboBox.currentTextChanged.connect(oOO_applicationState_OOo_nowWithUpdatedSecondStyleCombo)
style1ComboBox.currentTextChanged.connect(oOO_applicationState_OOo_nowWithUpdatedColorFieldStates)
style2ComboBox.currentTextChanged.connect(oOO_applicationState_OOo_nowWithUpdatedColorFieldStates)
oOO_applicationState_OOo_nowWithUpdatedSecondStyleCombo()
oOO_applicationState_OOo_nowWithUpdatedColorFieldStates()

row4Layout = QHBoxLayout()
addButton = QPushButton("Add Keyword")
addButton.clicked.connect(oOO_applicationState_OOo_nowWithAddedKeyword)
row4Layout.addWidget(addButton)
updateButton = QPushButton("Update Keyword")
updateButton.clicked.connect(oOO_applicationState_OOo_nowWithUpdatedKeyword)
updateButton.setEnabled(False)
row4Layout.addWidget(updateButton)
cancelButton = QPushButton("Cancel")
cancelButton.clicked.connect(oOO_applicationState_OOo_nowWithClearedSelection)
cancelButton.setEnabled(False)
row4Layout.addWidget(cancelButton)
addKeywordLayout.addLayout(row4Layout)

mainLayout.addWidget(addKeywordGroup, 0)
keywordsGroup = QGroupBox("Keywords List")
keywordsGroupLayout = QVBoxLayout()
keywordsGroup.setLayout(keywordsGroupLayout)
keywordsScrollArea = QScrollArea()
keywordsScrollArea.setWidgetResizable(True)
keywordsScrollAreaWidget = QWidget()
keywordsScrollAreaLayout = QVBoxLayout()
keywordsScrollAreaWidget.setLayout(keywordsScrollAreaLayout)
keywordsScrollAreaLayout.addStretch()
keywordsScrollArea.setWidget(keywordsScrollAreaWidget)
keywordsGroupLayout.addWidget(keywordsScrollArea)
mainLayout.addWidget(keywordsGroup, 1)
codeGroup = QGroupBox("Generated Lua Code")
codeGroupLayout = QVBoxLayout()
codeGroup.setLayout(codeGroupLayout)
codeTextEdit = QTextEdit()
codeTextEdit.setMaximumHeight(150)
codeGroupLayout.addWidget(codeTextEdit)
buttonsLayout = QHBoxLayout()
generateButton = QPushButton("Generate Lua Code")
generateButton.clicked.connect(oOO_applicationState_OOo_nowWithGeneratedLuaCode)
buttonsLayout.addWidget(generateButton)
copyButton = QPushButton("Copy to Clipboard")
copyButton.clicked.connect(oOO_clipboard_OOo_nowWithLuaCode)
buttonsLayout.addWidget(copyButton)
saveLuaButton = QPushButton("Save Lua to File")
saveLuaButton.clicked.connect(oOO_fileAtPath_OOo_nowWithLuaCode)
buttonsLayout.addWidget(saveLuaButton)
saveConfigButton = QPushButton("Save Configuration")
saveConfigButton.clicked.connect(oOO_fileAtPath_OOo_nowWithConfiguration)
buttonsLayout.addWidget(saveConfigButton)
loadConfigButton = QPushButton("Load Configuration")
loadConfigButton.clicked.connect(oOO_applicationState_OOo_nowWithLoadedConfiguration)
buttonsLayout.addWidget(loadConfigButton)
codeGroupLayout.addLayout(buttonsLayout)
mainLayout.addWidget(codeGroup, 0)
OAppO.show()
sys.exit(OApp.exec())
