// ============================================================
// PROGRAM: GifLoader
// TwinCAT 3 Structured Text
//
// Reads the CSV produced by the Python GIF converter and
// populates a 3D UDINT array for LED matrix playback.
//
// Required library: Tc2_Utilities
//   (FB_FileOpen, FB_FileGets, FB_FileClose, FOPEN_* constants)
//
// IMPORTANT: Place this program in a task with a cycle time
// of at least 50 ms to avoid watchdog timeouts while the
// WHILE loop parses the 2049 fields in each frame line.
//
// Usage:
//   1. Set sFilePath to the full path of your CSV file.
//   2. Pulse bLoad := TRUE for one cycle to start loading.
//   3. Wait for bBusy to go FALSE.
//   4. Check bDone (success) or bError + sErrorMsg (failure).
//   5. nFrameCount holds the number of frames actually loaded.
//
// Array layout  gifFrames[frame, row, col]:
//   frame : 0..200   (0 = first GIF frame)
//   row   : 0..31    (0 = bottom row, 31 = top row)
//   col   : 1..64    (1 = left column, 64 = right column)
//              col 0 is reserved / unused
//
// Pixel corners:
//   gifFrames[f,  0,  1] = bottom-left
//   gifFrames[f, 31,  1] = top-left
//   gifFrames[f,  0, 64] = bottom-right
//   gifFrames[f, 31, 64] = top-right
// ============================================================


// ============================================================
// DECLARATION  (paste into the declaration pane)
// ============================================================
VAR
    // --- Output ------------------------------------------------
    gifFrames   : ARRAY[0..200, 0..31, 0..64] OF UDINT;
    gifTimes    : ARRAY[0..200] OF UDINT;   // frame timestamps (ms)
    nFrameCount : INT;                       // frames successfully loaded

    // --- Control -----------------------------------------------
    bLoad     : BOOL;                        // pulse TRUE to begin loading
    sFilePath : STRING := 'C:\GifData\output.csv';

    // --- Status ------------------------------------------------
    bBusy     : BOOL;
    bDone     : BOOL;
    bError    : BOOL;
    sErrorMsg : STRING;
END_VAR

VAR
    // File I/O function blocks
    fbOpen  : FB_FileOpen;
    fbClose : FB_FileClose;
    fbGets  : FB_FileGets;
    hFile   : UINT;

    // State machine
    nState  : INT := 0;

    // Line buffers — sized for 2049 fields x ~9 chars each
    sLine   : STRING(20000);
    sRemain : STRING(20000);
    sField  : STRING(10);

    // Parsing counters
    nFrame  : INT;
    nPixel  : INT;   // 0 = timestamp column, 1..2048 = pixel columns
    nPos    : INT;
    nRow    : INT;
    nCol    : INT;
END_VAR


// ============================================================
// IMPLEMENTATION  (paste into the implementation pane)
// ============================================================
CASE nState OF

// ------------------------------------------------------------
0: // Idle — waiting for bLoad trigger
    IF bLoad THEN
        bLoad       := FALSE;
        nFrame      := 0;
        nFrameCount := 0;
        bBusy       := TRUE;
        bDone       := FALSE;
        bError      := FALSE;
        sErrorMsg   := '';
        nState      := 10;
    END_IF

// ------------------------------------------------------------
10: // Trigger file open
    fbOpen(bExecute  := TRUE,
           sPathName := sFilePath,
           nMode     := FOPEN_MODEREAD OR FOPEN_MODETEXT);
    nState := 11;

11: // Wait for file open to complete
    fbOpen(bExecute := FALSE);
    IF NOT fbOpen.bBusy THEN
        IF fbOpen.bError THEN
            bError    := TRUE;
            sErrorMsg := CONCAT('File open failed. ErrId: ', UDINT_TO_STRING(fbOpen.nErrId));
            nState    := 90;
        ELSE
            hFile  := fbOpen.hFile;
            nState := 20;
        END_IF
    END_IF

// ------------------------------------------------------------
20: // Trigger read of header row (discard it)
    fbGets(bExecute := TRUE, hFile := hFile, sLine := sLine);
    nState := 21;

21: // Wait for header read
    fbGets(bExecute := FALSE, hFile := hFile, sLine := sLine);
    IF NOT fbGets.bBusy THEN
        IF fbGets.bError OR fbGets.bEOF THEN
            bError    := TRUE;
            sErrorMsg := 'File is empty or header could not be read';
            nState    := 90;
        ELSE
            nState := 30;
        END_IF
    END_IF

// ------------------------------------------------------------
30: // Trigger read of one frame line
    IF nFrame > 200 THEN
        // Array is full — stop reading and close
        nFrameCount := nFrame;
        nState      := 90;
    ELSE
        fbGets(bExecute := TRUE, hFile := hFile, sLine := sLine);
        nState := 31;
    END_IF

31: // Wait for frame line read
    fbGets(bExecute := FALSE, hFile := hFile, sLine := sLine);
    IF NOT fbGets.bBusy THEN
        IF fbGets.bEOF OR LEN(sLine) = 0 THEN
            // End of file — all frames loaded
            nFrameCount := nFrame;
            nState      := 90;
        ELSIF fbGets.bError THEN
            bError    := TRUE;
            sErrorMsg := CONCAT('Read error at frame ', INT_TO_STRING(nFrame));
            nState    := 90;
        ELSE
            // Line ready — set up parser
            sRemain := sLine;
            nPixel  := 0;
            nState  := 40;
        END_IF
    END_IF

// ------------------------------------------------------------
40: // Parse all comma-separated fields from sRemain
    //
    // CSV column order (after time_ms):
    //   pixel 1..64   = row 1 (bottom), col 1..64
    //   pixel 65..128 = row 2,          col 1..64
    //   ...
    //   pixel 1985..2048 = row 32 (top), col 1..64
    //
    // Mapping to gifFrames[nFrame, nRow, nCol]:
    //   nPixel 0          -> timestamp -> gifTimes[nFrame]
    //   nPixel 1..2048    -> nRow = (nPixel-1) / 64       (0=bottom .. 31=top)
    //                        nCol = (nPixel-1) MOD 64 + 1 (1=left   .. 64=right)

    WHILE LEN(sRemain) > 0 AND nPixel <= 2048 DO

        nPos := FIND(sRemain, ',');
        IF nPos > 0 THEN
            sField  := LEFT(sRemain, nPos - 1);
            sRemain := RIGHT(sRemain, LEN(sRemain) - nPos);
        ELSE
            // Last field — no trailing comma
            sField  := sRemain;
            sRemain := '';
        END_IF

        IF nPixel = 0 THEN
            // First column is the frame timestamp
            gifTimes[nFrame] := STRING_TO_UDINT(sField);

        ELSE
            // Columns 1..2048 are pixel UDINT values
            nRow := (nPixel - 1) / 64;        // 0 (bottom) .. 31 (top)
            nCol := (nPixel - 1) MOD 64 + 1;  // 1 (left)   .. 64 (right)
            gifFrames[nFrame, nRow, nCol] := STRING_TO_UDINT(sField);
        END_IF

        nPixel := nPixel + 1;

    END_WHILE

    nFrame := nFrame + 1;
    nState := 30;   // read next frame

// ------------------------------------------------------------
90: // Trigger file close
    fbClose(bExecute := TRUE, hFile := hFile);
    nState := 91;

91: // Wait for file close
    fbClose(bExecute := FALSE);
    IF NOT fbClose.bBusy THEN
        nState := 99;
    END_IF

// ------------------------------------------------------------
99: // Done
    bBusy := FALSE;
    IF NOT bError THEN
        bDone := TRUE;
    END_IF
    nState := 0;

END_CASE
