PROGRAM PLC_PRG
VAR
	K0 AT %Q* : BOOL;
	APositive AT %Q* : BOOL;
	BPositive AT %Q* : BOOL;
	CPositive AT %Q* : BOOL;
	CNegative AT %Q* : BOOL;
	BNegative AT %Q* : BOOL;
	ANegative AT %Q* : BOOL;
	a0 AT %I* : BOOL;
	a1 AT %I* : BOOL;
	b1 AT %I* : BOOL;
	c1 AT %I* : BOOL;
	c0 AT %I* : BOOL;
	b0 AT %I* : BOOL;
	START : BOOL;
END_VAR

IF START THEN
IF START AND a0 AND NOT K0 THEN
	APositive := TRUE;
	IF a1 = True THEN
		BPositive := TRUE;
	END_IF;
	IF b1 = True THEN
		CPositive := TRUE;
	END_IF;
	IF c1 THEN
		K0 := TRUE;
	END_IF;

END_IF;


IF K0 THEN
	Apositive := FALSE;
	Bpositive := FALSE;
	Cpositive := FALSE;
END_IF;

IF c1 AND K0 THEN
	CNegative := TRUE;
	IF c0 THEN
		BNegative := TRUE;
	END_IF;
	IF b0 THEN
		ANegative := TRUE;
	END_IF;
	IF a0 THEN
		K0 := FALSE;
	END_IF;
	IF NOT K0 THEN
		Cnegative := FALSE;
		Bnegative := FALSE;
		Anegative := FALSE;
	END_IF;
END_IF;

END_IF;
