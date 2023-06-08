PROGRAM PLC_PRG
VAR
	K0 AT %Q* : BOOL;
	K1 AT %Q* : BOOL;
	K2 AT %Q* : BOOL;
	APositive AT %Q* : BOOL;
	ANegative AT %Q* : BOOL;
	BPositive AT %Q* : BOOL;
	BNegative AT %Q* : BOOL;
	b0 AT %I* : BOOL;
	a1 AT %I* : BOOL;
	a0 AT %I* : BOOL;
	b1 AT %I* : BOOL;
	START : BOOL;
END_VAR

IF START THEN
IF START AND b0 AND NOT K0 AND NOT K1 AND NOT K2 THEN
	APositive := TRUE;
	IF a1 THEN
		K0 := TRUE;
	END_IF;
END_IF;


IF K0 THEN
	Apositive := FALSE;
	Bnegative := FALSE;
END_IF;

IF a1 AND K0 THEN
	ANegative := TRUE;
END_IF;
IF a0 AND K1 THEN
	APositive := TRUE;
END_IF;
IF a1 AND K2 THEN
	ANegative := TRUE;
END_IF;

IF K0 THEN
	IF a0 THEN
		K1 := TRUE;
		K0 := FALSE;
	END_IF;
	IF NOT K0 THEN
		Anegative := FALSE;
	END_IF;
END_IF;


IF K1 THEN
	IF a1 THEN
		K2 := TRUE;
		K1 := FALSE;
	END_IF;
	IF NOT K1 THEN
		Anegative := FALSE;
	END_IF;
END_IF;


IF K2 THEN
	IF a0 THEN
		BPositive := TRUE;
	END_IF;
	IF b1 THEN
		K2 := FALSE;
	END_IF;
	IF NOT K2 THEN
		Anegative := FALSE;
	END_IF;
END_IF;

IF b1 AND NOT K0 AND NOT K1 AND NOT K2 THEN
	BNegative := TRUE;
END_IF;
END_IF;
