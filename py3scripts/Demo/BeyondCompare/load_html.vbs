Option Explicit

Sub loadHtml()
    Dim HTML As Object
    Dim WebEngine As Object
    Dim cws As Worksheet
    Dim ws As Worksheet
    Dim statusBarBack As Variant
    Dim savePath As String
    Dim urlColumn As String
    Dim nameColumn As String
    Dim sheetColumn As String
    Dim urlText As String
    Dim fileNameCell As String
    Dim fileNameCell2 As String
    Dim sheetName As String
    Dim startRow As Integer
    Dim stopRow As Integer
    Dim i As Integer
    
    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    
    ' Delete all other worksheet
    Set cws = ActiveSheet
    For i = Worksheets.Count To 1 Step -1
        If Worksheets(i).Name <> cws.Name Then
            Sheets(i).Select
            ActiveWindow.SelectedSheets.Delete
        End If
    Next i
    
    Set HTML = CreateObject("htmlfile")
    Set WebEngine = CreateObject("msxml2.xmlhttp")
    
    savePath = Range("E1").Value
    urlColumn = "A"
    nameColumn = "B"
    sheetColumn = "C"
    startRow = 2
    stopRow = cws.UsedRange.Rows.Count
    
    statusBarBack = Application.StatusBar
    For i = startRow To stopRow
        urlText = Range(urlColumn & i).Value
        If urlText <> "" Then
            ' Reason for -1 and -3: the first row and 1st~3rd columns will be deleted in the end
            fileNameCell = Cells(i, Range(nameColumn & i).Value).Address
            fileNameCell2 = Cells(i - 1, Range(nameColumn & i).Value - 3).Address
            sheetName = Range(sheetColumn & i).Value
            Sheets.Add after:=Worksheets(Worksheets.Count)
            Set ws = ActiveSheet
            ws.Name = sheetName
            
            WebEngine.Open "get", urlText, False
            WebEngine.Send
            CopyToClipbox WebEngine.ResponseText
            Cells(1, 1).Select
            ActiveSheet.Paste
            ' Move head part one column right
            Range("A1:A6").Select
            Selection.Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove
            ' Adjust column width
            Range("A:A,B:B,D:D,E:E").Select
            Selection.ColumnWidth = 4
            Range("C:C,F:F").Select
            Selection.ColumnWidth = 80
            Cells.Select
            Cells.EntireRow.AutoFit
            ' Apply cell pattern
            Columns("A:A").Select
            Selection.FormatConditions.AddColorScale ColorScaleType:=2
            Selection.FormatConditions(Selection.FormatConditions.Count).SetFirstPriority
            Selection.FormatConditions(1).ColorScaleCriteria(1).Type = _
                xlConditionValueLowestValue
            With Selection.FormatConditions(1).ColorScaleCriteria(1).FormatColor
                .Color = 16776444
                .TintAndShade = 0
            End With
            Selection.FormatConditions(1).ColorScaleCriteria(2).Type = _
                xlConditionValueHighestValue
            With Selection.FormatConditions(1).ColorScaleCriteria(2).FormatColor
                .Color = 8109667
                .TintAndShade = 0
            End With
            ' Add AutoFilter
            Rows("6:6").Select
            Selection.AutoFilter
            Range("A1").Select
            
            ' Add hyperlink
            Range("E1").Select
            ActiveSheet.Hyperlinks.Add Anchor:=Selection, Address:="", SubAddress:= _
                cws.Name & "!" & fileNameCell2, TextToDisplay:="Back"
            cws.Select
            Range(fileNameCell).Select
            ActiveSheet.Hyperlinks.Add Anchor:=Selection, Address:="", SubAddress:= _
                ws.Name & "!A1", TextToDisplay:=Range(fileNameCell).Value
        End If
        Application.StatusBar = "Current Row:" & i & " Max Row:" & stopRow
        DoEvents
    Next i
    Application.StatusBar = statusBarBack
    
    ' Delete FileUrl column
    Columns("A:C").Select
    Application.CutCopyMode = False
    Selection.Delete Shift:=xlToLeft
    Rows("1:1").Select
    Selection.Delete Shift:=xlUp
    Cells.Select
    Selection.ColumnWidth = 4
    Range("A1").Select
    
    ' Save without macro
    ActiveWorkbook.SaveAs FileName:=savePath, _
        FileFormat:=xlOpenXMLWorkbook, CreateBackup:=False
    
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
End Sub
Private Sub CopyToClipbox(strText As String)
    With CreateObject("new:{1C3B4210-F441-11CE-B9EA-00AA006B1A69}")
        .Clear
        .SetText strText
        .PutInClipboard
    End With
End Sub



