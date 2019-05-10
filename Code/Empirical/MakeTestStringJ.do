cap drop teststr
sca ptest=max(ptest,0.0001)
*gen teststr = "^{ "+substr("*",1,(.1/ptest)>1)+substr("*",1,(.05/ptest)>1)+substr("*",1,(0.01/ptest)>1)+"}"
gen teststr = ""
* Significance stars suppressed per AEJ:Macro policy, so this mini-script now does nothing.
