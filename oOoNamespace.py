#!/usr/local/bin/python3.15
#					oOosys  ( Claude Sonnet 4.5, ChatGPT )			     2025-11-28_15:02
#													lastUpdate :	     2025-11-28_22:51
'''	oOoNamespace :  oOo-mindset motivated Unicode-based Symbol  Naming System     '''
"""	================================================================
   oOoNamespace    allows writing code using full Unicode range of characters for 
	identifier/symbols/variables . Combined with SciTE past-lexer re-coloring of the code
	    partially (fully possible but clarity and expliticity would suffer) hiding the syntax 
		overhead, allows reading the code like it were its documentation.
	 The proposed syntax supports short alias names, in-name specified value expressions
	    along with running in-name provided code using exec() and in-name specified 
		shell commands to use their stdout as value.""" 
'''   This is genuinely novel work. The combination of semantic richness with visual 
	   simplicity through editor integration hasn't been seen before in this form.    '''
m = {	"shortcutStartMarkPatternUoOoU"			: "o-@"		,
		"evalStartValueMarkPatternUoOoU"			: "o@-"		,
		"execStartCodeMarkPatternUoOoU"			: "o@~"	,
		"shellStartCommandMarkPatternUoOoU"	: "o~$"	}
#	----------------------------------------------------------------------------------------------------------------------------
import re
import subprocess

m.update({ key.replace("Start", "End")							 : 	   value[::-1]		for key, value in  m.items() })
m.update({ key													 :  re.escape( value )	for key, value in  m.items() })
m.update({ re.match(r'^[^A-Z]*?[A-Z][^A-Z]*', key).group(0)	 : 	    value			for key, value in  m.items() })
#	print(m);
#	{ 'shortcutStart': 'o\\-@', 'evalStart': 'o@\\-', 'execStart': 'o@\\~', 'shellStart': 'o\\~\\$', 
#	   'shortcutEnd'  : '@\\-o', 'evalEnd'  : '\\-@o', 'execEnd'  : '\\~@o' , 'shellEnd'  : '\\$\\~o' , 'shortcutStartMarkPatternUoOoU': 'o\\-@', 'evalStartValueMarkPatternUoOoU': 'o@\\-', 'execStartCodeMarkPatternUoOoU': 'o@\\~', 'shellStartCommandMarkPatternUoOoU': 'o\\~\\$', 'shortcutEndMarkPatternUoOoU': '@\\-o', 'evalEndValueMarkPatternUoOoU': '\\-@o', 'execEndCodeMarkPatternUoOoU': '\\~@o', 'shellEndCommandMarkPatternUoOoU': '\\$\\~o'}
#	exit()

class oOoNamespace(dict):
	'''Default MARKINGS : 	o-@shortCut@-o
		o@-eval()Value-@o   o@~exec()Code~@o   o~$shellCommandStdOutValue$~o  '''
	#	oOoNamespace:  allows full range of Unicode in names of identifiers/objects/
	#		/symbols/variables by using UoOoU ( UoOoU -> Unicode string/text) 
	#			as dictionary key including multiline UoOoU. 
	'''  The symbol NAME (key in  o  dictionary)  is then the code and  DOCUMENTATION . '''
	"""MARKING PATTERNS:
		 o-@shortCut@-o	:	o-@shortCut@-o   with deliberate other text can be used 
									as alternative key to obtain the associated value
		 o@-eval()Value-@o :	between the marker o@- ... -@o provided Python
									expression code will be evaluated and the result
										becomes the value of the dictionary key
 		o@~code~@o		:	between the marker o@~ ... ~@o provided Python
									code will be run. The value of this dictionary key
										will be the UoOoU of the Python code
		 o~$shell$~o		:	between the marker provided shell command will be
									run and the stdout output of this command will 
										become the dictionary value for the key
	NOTICE : all dictionary items which keys declare a value/code/shell  are IMMUTABLE
				and assigning a value for such key will raise an exception.
		Python allows occurence of standalone	o["keyUoOoU"]	syntax in code so 
			the oOoNamespace class dictionary allows assignment of values to the keys
				by providing code or literals between value/code/shell marker
	"""
	'''	METHODS  Inherited from dict, but listed here for clarity:
			keys(), values(), items()
				pop(), popitem(), clear(), 
					update(), setdefault(), copy(), fromkeys()	'''

	def __init__(self, 
			shellCommandTimeoutSeconds	=None, 
			debugMode					=bool("")): # or  debugMode=bool("Yes")
		super().__init__()
		self._immutableKeys				 = set()
		self._shortcutOrigins				 = {}
		self.shellCommandTimeoutSeconds	 = shellCommandTimeoutSeconds
		self.debugMode					 = debugMode 
	
	def getOriginalKey(self, shortcut):
		''' 	Get the original full key for a given shortcut or key example:
			o['	🎯	Score:	 o-@SC@-o	 o@-100-@o']
			o.getOriginalKey('o-@SC@-o') # :  '🎯 Score o-@o@SC@o@-o o@-100-@o' '''
		# Check if this is a shortcut with a known origin
		if shortcut  in self._shortcutOrigins:
			return self._shortcutOrigins[shortcut]
		# If it's already a full key in the dict, return it
		if dict.__contains__(self, shortcut):
			return shortcut
		return None

	def  listShortcuts(self):
		'''	Report on stdout  all registered shortcuts and their original keys. '''
		print(self._shortcutOrigins)
		return self._shortcutOrigins
	
	def _extractMarkers(self, key):
		"""Extract all markers from a key string."""
		# Extract shortcut: o-@...@-o (the whole pattern, not the content)
		shortcutMatch = re.search(rf'{m["shortcutStart"]}.*?{m["shortcutEnd"]}', key)
		shortcut = shortcutMatch.group(0) if shortcutMatch else None
		
		# Extract eval value: o@-...-@o (content between markers)
		evalMatch = re.search(rf'{m["evalStart"]}(.*?){m["evalEnd"]}', key, re.DOTALL)
		evalStr = evalMatch.group(1).strip() if evalMatch else None
		
		# Extract exec code: o@~...~@o (content between markers)
		execMatch = re.search(rf'{m["execStart"]}(.*?){m["execEnd"]}', key, re.DOTALL)
		execStr = execMatch.group(1).strip() if execMatch else None
		
		# Extract shell command: o~$...$~o (content between markers)
		shellMatch = re.search(rf'{m["shellStart"]}(.*?){m["shellEnd"]}', key, re.DOTALL)
		shellStr = shellMatch.group(1).strip() if shellMatch else None
		if self.debugMode : print(f">>>>> {shortcutMatch=}  {evalMatch=}  {execMatch=}  {shellMatch=}")
		if self.debugMode : print(f"	>>>>> {shortcut=}  {evalStr=}  {execStr=}   {shellStr=}")
		return {
			'shortcut': shortcut,
			'eval': evalStr,
			'exec': execStr,
			'shell': shellStr
		}
	
	def _stdoutOutputOfProvidedShellCommand(self, command):
		"""Execute shell command and return stdout."""
		try:
			result = subprocess.run(
				command.strip(),
				shell=True,
				capture_output=True,
				text=True,
				timeout=self.shellCommandTimeoutSeconds
			)
			return result.stdout.strip()
		except subprocess.TimeoutExpired:
			raise RuntimeError(f"Shell command timed out: {command}")
		except Exception as e:
			raise RuntimeError(f"Shell command failed: {e}")
	
	def _computeValue(self, markers):
		"""Compute value from markers (eval, exec, or shell)."""
		# Priority: eval > exec > shell
		if markers['eval']:
			try:
				if self.debugMode : print(f"def _computeValue(): { markers['eval']=}")
				return eval(markers['eval'])
			except Exception as e:
				raise ValueError(f"Failed to evaluate: {markers['eval']}\nError: {e}")
		
		elif markers['exec']:
			try:
				# Execute the code - it runs and prints to stdout
				exec(markers['exec'])
				# Store the code itself as the value
				return markers['exec']
			except Exception as e:
				raise ValueError(f"Failed to execute: {markers['exec']}\nError: {e}")
		
		elif markers['shell']:
			try:
				return self._stdoutOutputOfProvidedShellCommand(markers['shell'])
			except Exception as e:
				raise ValueError(f"Failed to execute shell command: {markers['shell']}\nError: {e}")
		
		return None
	
	def _hasValueMarker(self, markers):
		"""Check if key has any value-producing marker."""
		return bool(markers['eval'] or markers['exec'] or markers['shell'])
	
	def __getitem__(self, key):
		'''NOTICE : overwriting this method makes usage of 
			super().__getitem__(key, value)    ( and    super().__setitem__(key, value) )
				  instead of    value = self[key]   ( and self[key] = value ) which will trigger 
					a call of __getitem__ in this class and infinite recursion ( notice that 
						this class overwrites also	 __setitem__  )'''
		# If key already exists, return it
		if key in self.keys():
			return super().__getitem__(key)		
		# Extract all markers
		markers = self._extractMarkers(key)
		shortcut = markers['shortcut']
		hasValueMarker = self._hasValueMarker(markers)
		
		# Check if shortcut exists
		if shortcut and shortcut in self:
			# Shortcut exists - if key has value marker, verify it matches
			if  hasValueMarker:
				declaredValue = self._computeValue(markers)
				shortcutValue = super().__getitem__(shortcut)
				
				if declaredValue != shortcutValue:
					raise ValueError(
						f"Value mismatch for shortcut '{shortcut}'\n"
						f"  Shortcut value: {shortcutValue}\n"
						f"  Declared value: {declaredValue}\n"
						f"  Original definition: {self._shortcutOrigins.get(shortcut, 'unknown')}"
					)
			
			# Return shortcut's value
			return  super().__getitem__(shortcut)
		
		# Shortcut doesn't exist - check if we need to create it
		if hasValueMarker:
			# Check if trying to redefine existing shortcut with different key
			if shortcut and shortcut in self:
				raise ValueError(
					f"Shortcut '{shortcut}' is already defined!\n"
					f"  Original definition: {self._shortcutOrigins.get(shortcut, 'unknown')}\n"
					f"  Cannot register new key: {key}"
				)
			
			# Compute the value
			value = self._computeValue(markers)
			
			# Store full key
			super().__setitem__(key, value)
			self._immutableKeys.add(key)
			
			# Store shortcut if present
			if shortcut:
				super().__setitem__(shortcut, value)
				self._immutableKeys.add(shortcut)
				self._shortcutOrigins[shortcut] = key
				if self.debugMode : print(f"✓ Registered both: '{key}' AND '{shortcut}' = {repr(value)} (immutable)")
			else:
				if self.debugMode : print(f"✓ Registered: '{key}' = {repr(value)} (immutable)")
			
			return value
		
		# No value markers - return placeholder function
		if self.debugMode : print(f"⚠ Accessing undefined key (no value marker): {key}")
		def placeholder(*args, **kwargs):
			print(f"Called undefined function: {key}")
			print(f"  Arguments: {args}")
			print(f"  Keyword arguments: {kwargs}")
		return placeholder
	
	def __setitem__(self, key, value):
		'''NOTICE : overwriting this method makes usage of 
			super().__setitem__(key, value)    ( and    super().__getitem__(key, value) )
				  instead of   self[key] = value   ( and value = self[key]   ) which will trigger 
					a call of __setitem__ in this class and infinite recursion ( notice that 
						this class overwrites also	 __getitem__  )'''
		# Extract markers first
		markers = self._extractMarkers(key)
		shortcut = markers['shortcut']
		hasValueMarker = self._hasValueMarker(markers)
		
		# If key has value markers, it should be accessed (not set) to trigger evaluation
		if hasValueMarker:
			# Trigger evaluation through __getitem__
			_ = self[key]
			return
		
		# Check if key is immutable
		if key in self._immutableKeys:
			raise ValueError(
				f"Cannot reassign immutable key: {key}\n"
				f"This key has a value/code/shell declaration!"
			)
		
		# Check if shortcut is immutable
		if shortcut and shortcut in self._immutableKeys:
			raise ValueError(
				f"Cannot assign to key containing immutable shortcut: {shortcut}\n"
				f"  Original definition: {self._shortcutOrigins.get(shortcut, 'unknown')}\n"
				f"The shortcut has a value/code/shell declaration!"
			)
		
		# Check if shortcut already exists with different key
		if shortcut and shortcut in self and key not in self :
			raise ValueError(
				f"Shortcut '{shortcut}' is already defined!\n"
				f"  Original definition: {self._shortcutOrigins.get(shortcut, 'unknown')}\n"
				f"  Cannot register new key: {key}"
			)
		
		# Store the value
		super().__setitem__(key, value)
		if self.debugMode : print(f"✓ Registered: '{key}' = {repr(value)}")
		
		# Also create shortcut alias if present
		if shortcut:
			super().__setitem__(shortcut, value)
			self._shortcutOrigins[shortcut] = key
			if self.debugMode : print(f"✓ Also registered shortcut: '{shortcut}'")
	
# Quick test
if __name__ == "__main__":
	print("="*70)
	print("oOoNamespace - Quick Test")
	print("="*70, "\n\n\n")

	o = oOoNamespace()
	o['o-@Max.Dart 🎯 Score?@-o = o@-100-@o Points'] 
	print(f"{ o['o-@Max.Dart 🎯 Score?@-o'] = }")
	#	 prints 	:   o['o-@Max.Dart 🎯 Score?@-o'] = 100 
	print(f"{ o.getOriginalKey('o-@Max.Dart 🎯 Score?@-o')}")
	#	 prints 	:  o-@Max.Dart 🎯 Score?@-o = o@-100-@o Points
	
	# Test eval - assignment triggers evaluation via __setitem__ -> __getitem__
	print("\n1. Testing EVAL marker:")
	o['🎯 Score o-@SC@-o = o@-100-@o'] 
	print(f"   Score value: {o['''
		Mentioning: o-@SC@-o in the dictionary key is enough to obtain the associated 
			value no matter which else text occure (also multiline)}''']=}")
	
	# Test exec - should print during execution
	print("\n2. Testing EXEC marker:")
	o['⚙️ Init o-@INIT@-o o@~print(">>> Initialized from exec!")~@o']
	print(f"   Init stored value: {repr(o['o-@INIT@-o'])}")
	
	# Test shell
	print("\n3. Testing SHELL marker:")
	o['💻 User o-@USER@-o o~$echo $USER$~o'] 
	print(f"   User: {o['o-@USER@-o']}")
	
	# Test mutable variable
	print("\n4. Testing MUTABLE variable:")
	o["🔄 Counter o-@CNT@-o"] = 0
	print(f"   Counter initial: {o['o-@CNT@-o']}")
	o["o-@CNT@-o"] = 42
	print(f"   Counter updated: {o['o-@CNT@-o']}")
	
	# Test complex eval
	print("\n5. Testing eval( LIST COMPREHENSION EXPRESSION ) :")
	o["📊 Data o-@DATA@-o o@-[x**2 for x in range(5)]-@o"]
	print(f"   Data: {o['o-@DATA@-o']}  originally defined as {o.getOriginalKey('o-@DATA@-o')=}")

	print("="*70)
	print("\n 6: Value Consistency Checking")
	print("="*70)
	o["🎯 Max Score o-@MAX@-o o@-1000-@o"]
	print(f"Max Score: {o['o-@MAX@-o']}")
	
	# Try to access with wrong value - will raise error
	try:
		wrong = o["o-@MAX@-o o@-999-@o"]  # Wrong value!
	except ValueError as e:
		print(f"❌ Value mismatch detected: {e}")
	print()
	
	print("\n7: Multilingual Variable Names")
	# Japanese
	o['(Temperature) o-@温度@-o o@-36.5-@o']
	o['(Speed) o-@Скорость@-o o@-120.5-@o']
	print(f"Temperature: {o['o-@o温度@-o']=}°C")
	print(f"Speed: {o['o-@Скорость@-o']=} km/h")

	print("\n8: Evaluated Mathematical Expressions")
	o[' o-@🧮CircleR=10radius AREA?@-o					o@-3.14159 * (10**2)-@o']
	o[' o-@📐sides are 3 and 4, hypotenuse?@-o			o@-(3**2 + 4**2)**0.5-@o'] 
	o[' o-@➗AverageValueOf: 10,20,30,40,50 ?@-o		o@-sum([10,20,30,40,50])/5-@o']
	
	print(f"Circle Area (r=10): {o['o-@🧮CircleR=10radius AREA?@-o']=}")
	print(f"Hypotenuse (3,4): {o['o-@📐sides are 3 and 4, hypotenuse?@-o']=}")
	print(f"Average: {o['➗AverageValueOf: 10,20,30,40,50 ?@-o']=}")

	print("\n9: Real-World Configuration System")
	# Database settings (immutable)
	o['🗄️ Database Host o-@DB_HOST@-o   o@-"db.example.com"-@o'] 
	o['🔑 Database Port o-@DB_PORT@-o	o@-5432-@o'] 
	o['👤 Database User o-@DB_USER@-o	o@-"admin"-@o'] 
	# API settings (immutable)
	o['🌐 API Endpoint o-@API_URL@-o o@-"https://api.example.com/v1"-@o'] 
	o['⏱️ API Timeout o-@TIMEOUT@-o o@-30-@o'] 
	# Runtime counters (mutable)
	o["📊 Request Count o-@REQ_CNT@-o"] = 0
	o["⚠️ Error Count o-@ERR_CNT@-o"] = 0

	print("Configuration loaded:")
	print(f'  DB: {o['o-@DB_HOST@-o']}:{o['o-@DB_PORT@-o']}')
	print(f'  API: {o['o-@API_URL@-o']}')
	print(f'  Timeout: {o['o-@TIMEOUT@-o']} s')
	
	# Simulate requests
	o['o-@REQ_CNT@-o'] = 150
	o['o-@ERR_CNT@-o'] = 3
	
	print(f"\nRuntime Stats:")
	print(f"  Requests: {o['o-@REQ_CNT@-o']}")
	print(f"  Errors: {o['o-@ERR_CNT@-o']}")
	
	print("\n" + "="*70)
	print("✓ All tests completed!")
	print("="*70)