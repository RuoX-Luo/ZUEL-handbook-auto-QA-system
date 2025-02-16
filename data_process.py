from PyPDF2 import PdfReader
import re
import os
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """从PDF文件中提取文本"""
    try:
        # 创建PDF Reader对象
        reader = PdfReader(pdf_path)
        
        # 提取所有页面的文本
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        return text
    except Exception as e:
        print(f"PDF文件读取错误: {str(e)}")
        return None

def clean_text(text):
    """清洗文本"""
    if text is None:
        return ""
    
    # 去除连续的点号
    text = re.sub(r'\.{3,}', '', text)
    
    # 去除页码标记
    text = re.sub(r'—\s*\d+\s*—', '', text)
    
    # 去除所有空白字符(包括空格、制表符、换行符等)
    text = re.sub(r'\s+', '', text)
    
    # 去除目录中的纯数字页码
    text = re.sub(r'\d+(?=\d)', '', text)
    
    # 统一替换中文标点
    text = text.replace('；', ';').replace('，', ',').replace('。', '.')
    
    return text.strip()

def split_text_into_blocks(text, min_size=500, max_size=800):
    """将文本分割成指定大小的块"""
    blocks = []
    
    # 按章节分割
    chapters = re.split(r'第[一二三四五六七八九十]+章\s*', text)
    
    for chapter in chapters:
        if not chapter.strip():
            continue
            
        # 按节分割
        sections = re.split(r'第[一二三四五六七八九十]+节\s*', chapter)
        
        for section in sections:
            if not section.strip():
                continue
                
            # 如果section超过最大长度，进一步分割
            if len(section) > max_size:
                current_block = ''
                sentences = re.split(r'[.。]', section)
                
                for sentence in sentences:
                    sentence = sentence.strip() + '.'
                    
                    if len(current_block) + len(sentence) <= max_size:
                        current_block += sentence
                    else:
                        if len(current_block) >= min_size:
                            blocks.append(current_block)
                            current_block = sentence
                        else:
                            current_block += sentence
                            
                if current_block and len(current_block) >= min_size:
                    blocks.append(current_block)
            else:
                blocks.append(section)
    
    return blocks

def save_blocks(blocks, output_dir):
    """保存文本块到文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    for i, block in enumerate(blocks, 1):
        block = block.strip()
        if not block:  # 跳过空块pip
            continue
            
        file_path = output_dir / f'block_{i:03d}.txt'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(block)
        saved_count += 1
            
    return saved_count

def process_pdf(pdf_path, output_dir='text_blocks', min_size=500, max_size=800):
    """PDF处理主函数"""
    # 打印处理开始信息
    print(f"开始处理PDF文件: {pdf_path}")
    
    # 1. 提取文本
    print("正在提取PDF文本...")
    text = extract_text_from_pdf(pdf_path)
    if text is None:
        return
    
    # 2. 清洗文本
    print("正在清洗文本...")
    cleaned_text = clean_text(text)
    
    # 3. 分块处理
    print("正在进行文本分块...")
    blocks = split_text_into_blocks(cleaned_text, min_size, max_size)
    
    # 4. 保存结果
    print("正在保存分块结果...")
    num_blocks = save_blocks(blocks, output_dir)
    
    # 打印处理完成信息
    print(f"\n处理完成!")
    print(f"共生成 {num_blocks} 个文本块")
    print(f"文本块保存在: {os.path.abspath(output_dir)}")
    
    # 返回块数量
    return num_blocks

def main():
    # 获取脚本文件的绝对路径
    script_path = os.path.abspath(__file__)
    # 获取脚本所在目录
    script_dir = os.path.dirname(script_path)
    
    # 更改工作目录到脚本所在目录
    os.chdir(script_dir)
    
    # 打印路径信息，方便调试
    print(f"脚本路径: {script_path}")
    print(f"脚本所在目录: {script_dir}")
    print(f"当前工作目录: {os.getcwd()}")
    print("目录中的文件:", os.listdir())
    
    # PDF文件路径
    pdf_path = 'ZUEL Student Handbook 2024.pdf'
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: 找不到PDF文件 '{pdf_path}'")
        return
    
    # 处理PDF文件
    process_pdf(pdf_path)

if __name__ == "__main__":
    main()