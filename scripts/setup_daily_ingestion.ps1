# PowerShell script to setup daily GCS ingestion on Windows Task Scheduler

Write-Host "Setting up daily GCS ingestion for Windows..." -ForegroundColor Green
Write-Host ""

# Get bucket name
$BUCKET_NAME = Read-Host "Enter your GCS bucket name"

if ([string]::IsNullOrWhiteSpace($BUCKET_NAME)) {
    Write-Host "ERROR: Bucket name is required" -ForegroundColor Red
    exit 1
}

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PYTHON_PATH = (Get-Command python).Source
$SCRIPT_PATH = Join-Path $SCRIPT_DIR "daily_gcs_ingestion.py"
$LOG_PATH = Join-Path $SCRIPT_DIR "daily_ingestion.log"

Write-Host ""
Write-Host "Task details:" -ForegroundColor Cyan
Write-Host "  Script: $SCRIPT_PATH"
Write-Host "  Python: $PYTHON_PATH"
Write-Host "  Bucket: $BUCKET_NAME"
Write-Host "  Log: $LOG_PATH"
Write-Host "  Schedule: Daily at 2:00 AM"
Write-Host ""

$CONFIRM = Read-Host "Create Windows Task Scheduler job? (y/n)"

if ($CONFIRM -eq "y" -or $CONFIRM -eq "Y") {
    # Create task action
    $ACTION = New-ScheduledTaskAction `
        -Execute $PYTHON_PATH `
        -Argument "$SCRIPT_PATH --bucket $BUCKET_NAME" `
        -WorkingDirectory $SCRIPT_DIR

    # Create task trigger (daily at 2 AM)
    $TRIGGER = New-ScheduledTaskTrigger -Daily -At 2am

    # Create task settings
    $SETTINGS = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable

    # Register the task
    $TASK_NAME = "FAHM-Daily-GCS-Ingestion"
    
    try {
        Register-ScheduledTask `
            -TaskName $TASK_NAME `
            -Action $ACTION `
            -Trigger $TRIGGER `
            -Settings $SETTINGS `
            -Description "Daily ingestion of new content from GCS bucket to Pinecone" `
            -Force

        Write-Host ""
        Write-Host "SUCCESS: Task created successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Task Name: $TASK_NAME" -ForegroundColor Cyan
        Write-Host "The script will run daily at 2:00 AM"
        Write-Host ""
        Write-Host "To view the task:" -ForegroundColor Yellow
        Write-Host "  Get-ScheduledTask -TaskName '$TASK_NAME'"
        Write-Host ""
        Write-Host "To run the task manually:" -ForegroundColor Yellow
        Write-Host "  Start-ScheduledTask -TaskName '$TASK_NAME'"
        Write-Host ""
        Write-Host "To remove the task:" -ForegroundColor Yellow
        Write-Host "  Unregister-ScheduledTask -TaskName '$TASK_NAME' -Confirm:`$false"
        Write-Host ""
    }
    catch {
        Write-Host "ERROR: Failed to create task - $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "Task not created" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green

# Made with Bob
