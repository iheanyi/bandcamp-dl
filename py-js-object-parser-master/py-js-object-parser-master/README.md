Simple JavaScript/ECMAScript object literal reader

Only supports object literals wrapped in `var x = ...;` statements, so you
  might want to do `read_js_object('var x = %s;' % literal)` if it's in another format.

Basic constant folding on strings and numbers is done, e.g. "hi " + "there!" reduces to "hi there!",
and 1+1 reduces to 2.

** Dependencies **

Requires the [slimit](http://github.com/rspivak/slimit) library for parsing.

** License **

Copyright (c) 2013 darkf

Licensed under the terms of the WTFPL:


	DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
 		Version 2, December 2004 
	
	Everyone is permitted to copy and distribute verbatim or modified 
	copies of this license document, and changing it is allowed as long 
	as the name is changed. 
	
	DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
	TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 
	
	  0. You just DO WHAT THE FUCK YOU WANT TO.