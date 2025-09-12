param (
    [Parameter(Mandatory=$true)]
    [string]$MdFilePath,
    
    [Parameter(Mandatory=$true)]
    [string]$Prefix,
    
    [Parameter(Mandatory=$false)]
    [switch]$KeepUnusedImages = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

function Write-Log {
    param (
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $coloredType = switch ($Type) {
        "INFO" { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor Cyan }
        "SUCCESS" { Write-Host "[$timestamp] [SUCCESS] $Message" -ForegroundColor Green }
        "WARNING" { Write-Host "[$timestamp] [WARNING] $Message" -ForegroundColor Yellow }
        "ERROR" { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
        default { Write-Host "[$timestamp] [$Type] $Message" }
    }
}

function Process-MdFile {
    param (
        [string]$MdFilePath,
        [string]$Prefix,
        [bool]$KeepUnusedImages,
        [bool]$DryRun
    )
    
    # 检查MD文件是否存在
    if (-not (Test-Path $MdFilePath)) {
        Write-Log "MD文件不存在: $MdFilePath" "ERROR"
        return $false
    }
    
    # 获取MD文件的目录
    $mdDir = Split-Path -Parent $MdFilePath
    $mdFileName = Split-Path -Leaf $MdFilePath
    
    # 检查pdf_images目录是否存在
    $imagesDir = Join-Path $mdDir "pdf_images"
    if (-not (Test-Path $imagesDir)) {
        Write-Log "图片目录不存在: $imagesDir" "ERROR"
        return $false
    }
    
    Write-Log "处理MD文件: $mdFileName"
    Write-Log "图片目录: $imagesDir"
    Write-Log "将添加前缀: $Prefix"
    
    if ($DryRun) {
        Write-Log "运行模式: 模拟运行 (不会实际修改文件)" "WARNING"
    } else {
        Write-Log "运行模式: 实际执行"
    }
    
    # 创建映射表
    $imageMapping = @{}
    $usedImages = @{}
    
    # 从MD文件中提取引用的图片
    $mdContent = Get-Content -Path $MdFilePath -Raw
    $pattern = 'pdf_images\\([^)]+)'
    $matches = [regex]::Matches($mdContent, $pattern)
    
    # 记录所有被引用的图片
    foreach ($match in $matches) {
        $imageName = $match.Groups[1].Value
        $usedImages[$imageName] = $true
    }
    
    Write-Log "在MD文件中找到 $($usedImages.Count) 个图片引用"
    
    # 获取所有图片文件
    $allImages = Get-ChildItem -Path $imagesDir -Filter "*.png"
    Write-Log "图片目录中共有 $($allImages.Count) 个PNG文件"
    
    $renamedCount = 0
    $deletedCount = 0
    $skippedCount = 0
    
    # 处理图片文件
    foreach ($image in $allImages) {
        if ($usedImages.ContainsKey($image.Name)) {
            # 检查图片名称是否已经包含前缀
            if ($image.Name -like "$Prefix*") {
                Write-Log "跳过已有前缀的图片: $($image.Name)" "WARNING"
                $skippedCount++
                continue
            }
            
            $newName = "$Prefix" + $image.Name
            $imageMapping[$image.Name] = $newName
            
            # 重命名文件
            if (-not $DryRun) {
                Rename-Item -Path $image.FullName -NewName $newName
            }
            Write-Log "重命名: $($image.Name) -> $newName" "SUCCESS"
            $renamedCount++
        } else {
            # 处理未使用的图片
            if (-not $KeepUnusedImages) {
                if (-not $DryRun) {
                    Remove-Item -Path $image.FullName
                }
                Write-Log "删除未使用的图片: $($image.Name)" "WARNING"
                $deletedCount++
            } else {
                Write-Log "保留未使用的图片: $($image.Name)" "INFO"
                $skippedCount++
            }
        }
    }
    
    # 更新MD文件中的引用
    $updatedContent = $mdContent
    foreach ($key in $imageMapping.Keys) {
        $updatedContent = $updatedContent -replace [regex]::Escape("pdf_images\$key"), "pdf_images\$($imageMapping[$key])"
    }
    
    # 保存更新后的MD文件
    if (-not $DryRun) {
        Set-Content -Path $MdFilePath -Value $updatedContent
    }
    
    # 输出统计信息
    Write-Log "处理完成!" "SUCCESS"
    Write-Log "重命名图片: $renamedCount" "SUCCESS"
    Write-Log "删除图片: $deletedCount" "WARNING"
    Write-Log "跳过图片: $skippedCount" "INFO"
    
    if (-not $DryRun) {
        Write-Log "MD文件已更新: $MdFilePath" "SUCCESS"
    } else {
        Write-Log "模拟运行完成，未实际修改文件" "WARNING"
    }
    
    return $true
}

# 主程序
try {
    $result = Process-MdFile -MdFilePath $MdFilePath -Prefix $Prefix -KeepUnusedImages $KeepUnusedImages -DryRun $DryRun
    
    if ($result) {
        exit 0
    } else {
        exit 1
    }
} catch {
    Write-Log "发生错误: $_" "ERROR"
    exit 1
}