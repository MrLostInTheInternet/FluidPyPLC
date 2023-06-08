PROGRAM PLC_PRG
VAR
	K0 : BOOL;
	APositive : BOOL;
	BPositive : BOOL;
	CPositive : BOOL;
	CNegative : BOOL;
	ANegative : BOOL;
	BNegative : BOOL;
	b0 : BOOL;
	a1 : BOOL;
	b1 : BOOL;
	c1 : BOOL;
	c0 : BOOL;
	a0 : BOOL;
	START : BOOL;
END_VAR

IF START THEN
IF START AND b0 AND NOT K0 THEN
	APositive := TRUE;
END_IF;

IF START AND NOT K0 THEN
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
END_IF;


IF K0 THEN
	IF c0 THEN
		ANegative := TRUE;
	IF a0 THEN
		BNegative := TRUE;
	END_IF;
	END_IF;
	IF b0 THEN
		K0 := FALSE;
	END_IF;
	IF NOT K0 THEN
		Cnegative := FALSE;
		Anegative := FALSE;
		Bnegative := FALSE;
	END_IF;
END_IF;

END_IF;
