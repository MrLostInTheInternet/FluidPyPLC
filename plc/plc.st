PROGRAM PLC_PRG
VAR
	K0 AT %Q* : BOOL;
	K1 AT %Q* : BOOL;
	K2 AT %Q* : BOOL;
	K3 AT %Q* : BOOL;
	K4 AT %Q* : BOOL;
	K5 AT %Q* : BOOL;
	APositive AT %Q* : BOOL;
	ANegative AT %Q* : BOOL;
	CPositive AT %Q* : BOOL;
	CNegative AT %Q* : BOOL;
	DPositive AT %Q* : BOOL;
	DNegative AT %Q* : BOOL;
	d0 AT %I* : BOOL;
	a1 AT %I* : BOOL;
	a0 AT %I* : BOOL;
	c1 AT %I* : BOOL;
	c0 AT %I* : BOOL;
	d1 AT %I* : BOOL;
	START : BOOL;
END_VAR

IF START THEN
IF START AND d0 AND NOT K0 AND NOT K1 AND NOT K2 AND NOT K3 AND NOT K4 AND NOT K5 THEN
	APositive := TRUE;
	IF a1 THEN
		K0 := TRUE;
	END_IF;
END_IF;


IF K0 THEN
	Apositive := FALSE;
	Dnegative := FALSE;
END_IF;

IF a1 AND K0 THEN
	ANegative := TRUE;
	IF a0 THEN
		K1 := TRUE;
		K0 := FALSE;
	END_IF;
	IF NOT K0 THEN
		Anegative := FALSE;
	END_IF;
END_IF;

IF a0 AND K1 THEN
	APositive := TRUE;
	IF a1 THEN
		K2 := TRUE;
		K1 := FALSE;
	END_IF;
	IF NOT K1 THEN
		Anegative := FALSE;
	END_IF;
END_IF;

IF a1 AND K2 THEN
	ANegative := TRUE;
	IF a0 THEN
		CPositive := TRUE;
	END_IF;
	IF c1 THEN
		K3 := TRUE;
		K2 := FALSE;
	END_IF;
	IF NOT K2 THEN
		Anegative := FALSE;
	END_IF;
END_IF;

IF c1 AND K3 THEN
	CNegative := TRUE;
	IF c0 THEN
		K4 := TRUE;
		K3 := FALSE;
	END_IF;
	IF NOT K3 THEN
		Anegative := FALSE;
	END_IF;
END_IF;

IF c0 AND K4 THEN
	CPositive := TRUE;
	IF c1 THEN
		K5 := TRUE;
		K4 := FALSE;
	END_IF;
	IF NOT K4 THEN
		Anegative := FALSE;
	END_IF;
END_IF;

IF c1 AND K5 THEN
	CNegative := TRUE;
	IF c0 THEN
		DPositive := TRUE;
	END_IF;
	IF d1 THEN
		K5 := FALSE;
	END_IF;
	IF NOT K5 THEN
		Anegative := FALSE;
	END_IF;
END_IF;

IF d1 AND NOT K0 AND K1 = False AND K2 = False AND K3 = False AND K4 = False AND K5 = False THEN
	DNegative := TRUE;
END_IF;
END_IF;
