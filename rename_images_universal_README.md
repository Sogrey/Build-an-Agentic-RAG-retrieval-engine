# MD文件图片批量重命名工具

这个PowerShell脚本用于处理Markdown文件中引用的图片，可以批量添加前缀并更新MD文件中的引用路径。它还可以选择性地删除未被引用的图片，帮助清理项目目录。

## 功能特点

- **自动检测**：自动识别MD文件中引用的所有图片
- **批量重命名**：为所有引用的图片添加指定前缀
- **智能更新**：自动更新MD文件中的所有图片引用路径
- **清理功能**：可选择性地删除未被引用的图片
- **模拟运行**：支持模拟运行模式，预览将要进行的更改而不实际修改文件
- **详细日志**：提供彩色格式化的日志输出，显示处理进度和结果统计

## 系统要求

- PowerShell 5.0 或更高版本
- Windows 7/10/11 或 Windows Server 2012 R2 或更高版本
- 也可在安装了PowerShell Core的Linux或macOS上运行

## 使用方法

### 基本用法

```powershell
.\rename_images_universal.ps1 -MdFilePath "路径/到/你的文件.md" -Prefix "你想要的前缀-"
```

### 参数说明

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `-MdFilePath` | 字符串 | 是 | 要处理的Markdown文件的路径 |
| `-Prefix` | 字符串 | 是 | 要添加到图片名称前的前缀 |
| `-KeepUnusedImages` | 开关 | 否 | 设置此参数可保留未在MD文件中引用的图片 |
| `-DryRun` | 开关 | 否 | 设置此参数可进行模拟运行，不实际修改任何文件 |

### 高级用法示例

#### 保留未使用的图片

```powershell
.\rename_images_universal.ps1 -MdFilePath "文档/我的文档.md" -Prefix "项目名称-" -KeepUnusedImages
```

#### 模拟运行（不实际修改文件）

```powershell
.\rename_images_universal.ps1 -MdFilePath "文档/我的文档.md" -Prefix "项目名称-" -DryRun
```

#### 组合参数

```powershell
.\rename_images_universal.ps1 -MdFilePath "文档/我的文档.md" -Prefix "项目名称-" -KeepUnusedImages -DryRun
```

## 工作原理

1. 脚本首先检查指定的MD文件是否存在
2. 然后检查同目录下是否存在`pdf_images`文件夹
3. 从MD文件中提取所有图片引用（格式为`![Image](pdf_images\filename.png)`）
4. 为每个被引用的图片添加指定前缀
5. 根据设置决定是否删除未被引用的图片
6. 更新MD文件中的所有图片引用路径
7. 输出详细的处理统计信息

## 注意事项

- 脚本默认会删除未在MD文件中引用的图片，如果想保留这些图片，请使用`-KeepUnusedImages`参数
- 脚本会跳过已经包含指定前缀的图片
- 脚本只处理PNG格式的图片，如需处理其他格式，请修改脚本中的`-Filter "*.png"`部分
- 脚本假设图片引用格式为`![Image](pdf_images\filename.png)`，如果使用其他格式，可能需要调整正则表达式

## 示例场景

### 场景1：为项目文档添加统一前缀

假设你有一个项目文档`项目说明.md`，其中引用了多张图片，你想为所有图片添加项目名称作为前缀：

```powershell
.\rename_images_universal.ps1 -MdFilePath "项目说明.md" -Prefix "ProjectX-"
```

### 场景2：在修改前预览更改

在对重要文档进行操作前，你可能想先预览将要进行的更改：

```powershell
.\rename_images_universal.ps1 -MdFilePath "重要文档.md" -Prefix "V2-" -DryRun
```

### 场景3：整理多个文档的图片

如果你有多个文档需要处理，可以结合使用批处理或循环：

```powershell
$docs = @("文档1.md", "文档2.md", "文档3.md")
$prefixes = @("Doc1-", "Doc2-", "Doc3-")

for ($i = 0; $i -lt $docs.Length; $i++) {
    .\rename_images_universal.ps1 -MdFilePath $docs[$i] -Prefix $prefixes[$i]
}
```

## 故障排除

如果遇到问题，请尝试以下步骤：

1. 使用`-DryRun`参数进行模拟运行，检查预期的更改
2. 确保有足够的权限访问和修改相关文件和目录
3. 检查MD文件中的图片引用格式是否符合脚本的预期
4. 如果脚本无法识别图片引用，可能需要调整正则表达式

## 贡献与改进

欢迎提出改进建议或贡献代码。可能的改进方向：

- 支持更多图片格式（如jpg, gif等）
- 支持更多图片引用格式
- 添加备份功能
- 添加撤销功能

## 许可

MIT License