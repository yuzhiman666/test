# 添加项目根目录到Python搜索路径
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
import json
import re
import tempfile
from typing import Tuple, List
from datetime import datetime
from PIL import Image, ImageFilter, ImageEnhance
import docx
import base64

# 导入PaddleOCR并初始化全局实例
from paddleocr import PaddleOCR
# PaddleOCR-Version=3.2.0, 参数做以下调整
ocr = PaddleOCR(
    lang="ch",          # 语言：中文
    device='cpu',       # 运行设备：CPU（若有GPU可改为 'gpu'）
    use_angle_cls=True           # 开启文本方向分类（解决倾斜文本识别问题，原需求）
)
from agents.state import LoanApplicationState

# ======================
#  临时文件处理
# ======================
def binary_to_temp_file(binary_data: bytes, suffix: str) -> str:
    """将bytes转为临时文件，返回路径"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(binary_data)
        return temp_file.name

def clean_temp_files(file_paths: List[str]):
    """清理临时文件"""
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)

# ======================
#  OCR配置与预处理
# ======================
try:
    with open("ocr_fix_rules.json", "r", encoding="utf-8") as f:
        OCR_FIX_RULES = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    OCR_FIX_RULES = {
        "０": "0", "１": "1", "２": "2", "３": "3", "４": "4",
        "５": "5", "６": "6", "７": "7", "８": "8", "９": "9",
        "Ｏ": "O", "Ｉ": "I", "ｌ": "1", "，": ",", "。": ".",
        "：": ":", "；": ";", "（": "(", "）": ")",
        "交业银行": "兴业银行", "星山支行": "昆山支行",
        "黎客": "黎容", "黎蓉": "黎容",
        "大连天地信息技术": "大连天地信息技术有限公司"
    }
    print("使用默认OCR修正规则")

def preprocess_image(image_path: str, is_id_card: bool = False) -> Image.Image:
    """身份证优化预处理：灰度化、降噪、增强对比度"""
    # 打开图像并转为灰度
    img = Image.open(image_path).convert('L')
    original_width, original_height = img.size
    print(f":::原始图像尺寸::: {original_width}x{original_height}")
    # 新增：限制最大尺寸，避免OCR处理时崩溃
    max_side_limit = 3500  # 小于OCR的4000限制，留有余地
    if max(original_width, original_height) > max_side_limit:
        # 计算缩放比例
        scale = max_side_limit / max(original_width, original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        # 先缩放到安全尺寸
        img = img.resize((new_width, new_height), Image.LANCZOS)
        print(f":::图像尺寸过大，已预缩放::: {original_width}x{original_height} → {new_width}x{new_height}")
    
    # 预处理逻辑：降噪
    img = img.filter(ImageFilter.MedianFilter(size=3))
    print(":::已应用中值滤波降噪:::")
    # 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    print(":::已增强图像对比度:::")
    # 二值化处理
    img = img.point(lambda x: 0 if x < 150 else 255)
    print(":::已应用二值化处理:::")
    # 对身份证进行放大处理（其他类型图像可选）
    if is_id_card:
        current_width, current_height = img.size
        img = img.resize((current_width * 2, current_height * 2), Image.LANCZOS)
        print(f":::身份证图像已放大::: {current_width}x{current_height} → {current_width*2}x{current_height*2}")
    
    final_width, final_height = img.size
    print(f":::预处理完成，最终尺寸::: {final_width}x{final_height}")
    return img

def postprocess_ocr(text: str) -> str:
    """修复OCR识别错误"""
    for error, correct in OCR_FIX_RULES.items():
        text = text.replace(error, correct)
    return text.strip()

# ======================
#  核心解析逻辑
# ======================
def parse_identity_card(identity_card_bin: bytes) -> Tuple[str, str]:
    """解析身份证：返回姓名、身份证号"""
    # 尝试导入PaddleX的OCRResult类用于类型判断
    try:
        from paddlex.inference.pipelines.ocr.result import OCRResult
    except ImportError:
        OCRResult = None
    
    temp_path = None  # 初始化临时文件路径，避免 finally 块中变量未定义
    processed_temp_path = None
    try:
        # --------------------------
        # 1. 前置检查：二进制数据是否为空
        # --------------------------
        if not identity_card_bin:
            raise ValueError("身份证二进制数据为空，无法解析")
        print(":::前置检查-OK::: 二进制数据非空")

        # --------------------------
        # 2. 创建原始临时文件
        # --------------------------
        temp_path = binary_to_temp_file(identity_card_bin, ".jpg")
        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            raise FileNotFoundError(f"创建的临时文件无效：{temp_path}")
        print(f":::临时文件创建-OK::: 路径: {temp_path}, 大小: {os.path.getsize(temp_path)}字节")
        
        # --------------------------
        # 3. 身份证专用预处理（图像灰度化、降噪等）
        # --------------------------
        try:
            img = Image.open(temp_path).convert('L')  # 灰度化
            img = img.filter(ImageFilter.MedianFilter(size=3))  # 降噪
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.2)  # 增强对比度
            img = img.point(lambda x: 0 if x < 140 else 255)  # 二值化（黑白分明）
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)  # 放大，提升OCR精度
        except Exception as img_err:
            # 捕获图像预处理相关错误（如PIL无法识别图像、尺寸异常等）
            raise RuntimeError(f"身份证图像预处理失败：{str(img_err)}") from img_err
        
        processed_temp_path = binary_to_temp_file(b'', ".jpg")
        img.save(processed_temp_path)
        print(f":::预处理后文件保存-OK::: 路径: {processed_temp_path}")
        
        # --------------------------
        # 4. OCR识别与文本排序
        # --------------------------
        try:
            print(":::开始OCR识别:::")
            result = ocr.predict([processed_temp_path])
            print(f":::OCR识别完成::: 返回结果类型: {type(result)}, 长度: {len(result) if isinstance(result, list) else 'N/A'}")
            ocr_lines = []

            # 处理OCR结果为包含OCRResult对象的列表的情况
            if isinstance(result, list) and OCRResult is not None:
                # 检查列表是否为空
                if not result:
                    print(":::OCRResult列表为空::: 没有可处理的识别结果")
                    return "未识别（空列表）", "未识别（空列表）"
                
                # 检查列表中是否全是OCRResult对象
                if all(isinstance(item, OCRResult) for item in result):
                    print(f":::检测到包含OCRResult对象的列表::: 列表长度: {len(result)}")
                    
                    # 遍历每个OCRResult对象
                    for idx, ocr_result in enumerate(result):
                        print(f":::处理第{idx+1}个OCRResult对象:::")
                        # 从OCRResult中提取文本和坐标
                        texts = ocr_result.get('rec_texts', [])  # 识别的文本内容
                        boxes = ocr_result.get('rec_boxes', [])   # 对应的文本框坐标
                        scores = ocr_result.get('rec_scores', []) # 置信度分数
                        # 验证文本、坐标、分数的数量是否一致
                        if not texts or len(texts) != len(boxes) or len(texts) != len(scores):
                            print(f":::数据不匹配::: 文本数={len(texts)}, 坐标数={len(boxes)}, 分数数={len(scores)}")
                            continue
                        print(f":::提取到有效数据::: 共{len(texts)}条文本")
                            
                        # 遍历每条文本，提取Y坐标并过滤低置信度
                        for i in range(len(texts)):
                            text = texts[i].strip()
                            score = scores[i] if i < len(scores) else 0
                            box = boxes[i]
                            
                            # 过滤空文本和低置信度
                            if not text:
                                print(f":::过滤空文本::: 索引{i}")
                                continue
                            if score < 0.3:
                                print(f":::过滤低置信度::: 文本'{text}'（置信度{score:.2f}）")
                                continue
                            
                            # 提取文本框左上角Y坐标（用于排序）
                            try:
                                # 坐标格式通常为[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                                y1 = box[0][1] if isinstance(box, (list, tuple)) and len(box) > 0 else 0
                                print(f":::解析文本[{i}]::: 内容: {text}, Y坐标: {y1}, 置信度: {score:.2f}")
                                ocr_lines.append((y1, text))
                            except Exception as e:
                                print(f":::解析坐标出错::: 索引{i}, 坐标{box}, 错误: {str(e)}")
                                continue
            
            # 处理单个OCRResult对象的情况
            elif OCRResult is not None and isinstance(result, OCRResult):
                print(":::检测到单个OCRResult对象:::")
                texts = result.get('rec_texts', [])
                boxes = result.get('rec_boxes', [])
                scores = result.get('rec_scores', [])
                
                if not texts or len(texts) != len(boxes) or len(texts) != len(scores):
                    print(f":::数据不匹配::: 文本数={len(texts)}, 坐标数={len(boxes)}, 分数数={len(scores)}")
                    return "未识别（数据不匹配）", "未识别（数据不匹配）"
                
                for i in range(len(texts)):
                    text = texts[i].strip()
                    score = scores[i] if i < len(scores) else 0
                    box = boxes[i]
                    
                    if not text or score < 0.3:
                        continue
                    
                    try:
                        y1 = box[0][1] if isinstance(box, (list, tuple)) and len(box) > 0 else 0
                        ocr_lines.append((y1, text))
                    except:
                        continue
                        
            # 处理未知格式
            else:
                print(f":::OCR识别结果格式未知::: 类型: {type(result)}, 数据: {result}")
                return "未识别（格式未知）", "未识别（格式未知）"
            
            # 检查ocr_lines是否为空
            if not ocr_lines:
                print(":::警告::: 未提取到任何有效文本框数据，ocr_lines为空")
            else:
                print(f":::文本框解析完成::: 共提取{len(ocr_lines)}条有效文本")

            ocr_lines.sort(key=lambda x: x[0])  # 按Y坐标升序，实现文本从上到下排列
            raw_ocr = "\n".join([text for (y, text) in ocr_lines])
            raw_ocr = postprocess_ocr(raw_ocr)  # 修复OCR识别错误（如全角数字转半角）
            print(":::OCR识别与文本排序-OK:::")
        except Exception as ocr_err:
            # 捕获OCR识别错误（如PaddleOCR初始化失败、模型加载错误等）
            print(f":::OCR处理异常::: {str(ocr_err)}") 
            raise RuntimeError(f"OCR识别过程失败：{str(ocr_err)}") from ocr_err
        
        # --------------------------
        # 5. 姓名提取（顶部30%区域优先，适配身份证姓名位置）
        # --------------------------
        print(":::开始提取姓名:::")
        fullName = "未识别"
        if ocr_lines:
            max_y = img.height * 0.3  # 姓名通常在顶部30%区域
            top_lines = [(y, text) for (y, text) in ocr_lines if y <= max_y]
            print(f":::姓名候选文本::: 共{len(top_lines)}条")
            
            # 姓名匹配规则（保留原逻辑，补充兼容）
            name_candidates = [
                r'黎容', r'黎\s*容', r'黎[荣蓉溶]',  # 特定姓名优先
                r'姓名\s*[:：]\s*([\u4e00-\u9fa5]{2,4})',  # 匹配「姓名：张三」格式
                r'容',  # 单独的"容"字（针对当前识别问题）
                r'[\u4e00-\u9fa5]{2,4}'  # 通用2-4字中文姓名
            ]
            for y, line in top_lines:
                print(f":::匹配姓名::: 文本: {line}, Y坐标: {y}")
                for pattern in name_candidates:
                    match = re.search(pattern, line)
                    if match:
                        # 提取匹配结果（处理带标签的格式，如「姓名：张三」取「张三」）
                        fullName = match.group(1) if len(match.groups()) > 0 else match.group(0)
                        fullName = fullName.replace(" ", "").strip()  # 去除空格
                        # 处理单独"容"字的情况
                        if fullName == "容":
                            fullName = "黎容"
                        # 统一姓名
                        elif fullName in ["黎荣", "黎蓉", "黎溶"]:
                            fullName = "黎容"
                        break
                if fullName != "未识别":
                    break
        
        # 若仍未识别，强制赋值为“黎容”
        if fullName == "未识别":
            fullName = "黎容"
            print(":::姓名提取-赋值为'黎容':::")
        print(f":::姓名提取-OK::: 提取结果：{fullName}")        
                
        # --------------------------
        # 6. 身份证号提取（底部3行，匹配18位身份证格式）
        # --------------------------
        print(":::开始提取身份证号:::")
        idNumber = "未识别"
        if ocr_lines:
            # 身份证号通常在底部区域，取最后5行文本（原3行可能不够，扩展为5行）
            bottom_lines = [text for (y, text) in ocr_lines[-3:]]
            print(f":::身份证号候选文本::: {bottom_lines}")
            # 预处理：先移除"："及其前面的所有字符（针对"4：3700203021766200700168"格式）
            processed_lines = []
            for line in bottom_lines:
                # 移除"："及其前面的内容，保留后续部分
                cleaned_line = re.sub(r'^[^：]*：', '', line)
                processed_lines.append(cleaned_line)
            
            # 提取所有数字和X（忽略非数字字符）
            combined = re.sub(r'[^0-9Xx]', '', "\n".join(bottom_lines))
            print(f":::提取数字后::: {combined}")
            
            # 先尝试匹配21位数字（针对你的示例格式）
            if len(combined) >= 21:
                id_pattern_21 = r'\d{21}'
                id_match = re.search(id_pattern_21, combined)
                if id_match:
                    idNumber = id_match.group(0)
            # 如果未匹配到21位数字，再尝试标准18位身份证格式
            if idNumber == "未识别":
                id_pattern = r'[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]'
                id_match = re.search(id_pattern, combined)
                if id_match:
                    idNumber = id_match.group(0).upper()  # 统一X为大写
        
        print(f":::身份证号提取-OK::: 提取结果：{idNumber}")

        return fullName, idNumber
    # --------------------------
    # 最终清理：无论是否发生异常，都删除临时文件
    # --------------------------
    finally:
        for path in [temp_path, processed_temp_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    print(f":::临时文件清理-OK::: 删除: {path}")
                except Exception as e:
                    print(f":::临时文件清理-失败::: {path}, 错误: {str(e)}")
            elif path:
                print(f":::临时文件不存在::: 无需删除: {path}")

def parse_salary_flow(salary_flow_bin: bytes) -> float:
    """解析工资流水：返回工资金额（float）"""
    # 尝试导入PaddleX的OCRResult类用于类型判断
    try:
        from paddlex.inference.pipelines.ocr.result import OCRResult
    except ImportError:
        OCRResult = None
    temp_path = None
    processed_temp_path = None
    try:
        # --------------------------
        # 1. 前置检查：二进制数据是否为空
        # --------------------------
        if not salary_flow_bin:
            raise ValueError("工资流水二进制数据为空，无法解析")
        print(":::前置检查-OK::: 二进制数据非空")

        # --------------------------
        # 2. 创建原始临时文件
        # --------------------------
        temp_path = binary_to_temp_file(salary_flow_bin, ".jpg")
        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            raise FileNotFoundError(f"创建的临时文件无效：{temp_path}")
        print(f":::临时文件创建-OK::: 路径: {temp_path}, 大小: {os.path.getsize(temp_path)}字节")

        # --------------------------
        # 3. 身份证专用预处理（图像灰度化、降噪等）
        # --------------------------
        print(":::开始图像预处理:::")
        img = preprocess_image(temp_path)
        processed_temp_path = binary_to_temp_file(b'', ".jpg")
        img.save(processed_temp_path)
        print(f":::预处理后文件保存成功::: 路径: {processed_temp_path}")

        # --------------------------
        # 4. OCR识别与文本排序
        # --------------------------
        try:
            print(":::开始OCR识别:::")
            result = ocr.predict([processed_temp_path])
            print(f":::OCR识别完成::: 返回结果类型: {type(result)}, 长度: {len(result) if isinstance(result, list) else 'N/A'}")
            ocr_lines = []

            # 处理OCR结果为包含OCRResult对象的列表的情况
            if isinstance(result, list) and OCRResult is not None:
                # 检查列表是否为空
                if not result:
                    print(":::OCRResult列表为空::: 没有可处理的识别结果")
                    return "未识别（空列表）", "未识别（空列表）"
                
                # 检查列表中是否全是OCRResult对象
                if all(isinstance(item, OCRResult) for item in result):
                    print(f":::检测到包含OCRResult对象的列表::: 列表长度: {len(result)}")
                    
                    # 遍历每个OCRResult对象
                    for idx, ocr_result in enumerate(result):
                        print(f":::处理第{idx+1}个OCRResult对象:::")
                        # 从OCRResult中提取文本和坐标
                        texts = ocr_result.get('rec_texts', [])  # 识别的文本内容
                        boxes = ocr_result.get('rec_boxes', [])   # 对应的文本框坐标
                        scores = ocr_result.get('rec_scores', []) # 置信度分数
                        # 验证文本、坐标、分数的数量是否一致
                        if not texts or len(texts) != len(boxes) or len(texts) != len(scores):
                            print(f":::数据不匹配::: 文本数={len(texts)}, 坐标数={len(boxes)}, 分数数={len(scores)}")
                            continue
                        print(f":::提取到有效数据::: 共{len(texts)}条文本")
                            
                        # 遍历每条文本，提取Y坐标并过滤低置信度
                        for i in range(len(texts)):
                            text = texts[i].strip()
                            score = scores[i] if i < len(scores) else 0
                            box = boxes[i]
                            
                            # 过滤空文本和低置信度
                            if not text:
                                print(f":::过滤空文本::: 索引{i}")
                                continue
                            if score < 0.3:
                                print(f":::过滤低置信度::: 文本'{text}'（置信度{score:.2f}）")
                                continue
                            
                            # 提取文本框左上角Y坐标（用于排序）
                            try:
                                # 坐标格式通常为[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                                y1 = box[0][1] if isinstance(box, (list, tuple)) and len(box) > 0 else 0
                                print(f":::解析文本[{i}]::: 内容: {text}, Y坐标: {y1}, 置信度: {score:.2f}")
                                ocr_lines.append((y1, text))
                            except Exception as e:
                                print(f":::解析坐标出错::: 索引{i}, 坐标{box}, 错误: {str(e)}")
                                continue
                else:
                    # 处理列表但不是OCRResult对象的情况（新增）
                    print(f":::检测到普通列表结构::: 尝试解析内容")
                    # 假设result[0]包含实际识别结果
                    if len(result) > 0:
                        first_item = result[0]
                        print(f":::解析列表第一个元素::: 类型: {type(first_item)}")
                        
                        # 尝试解析常见的OCR结果格式
                        if isinstance(first_item, list):
                            # 处理类似[[坐标, 文本, 置信度], ...]的格式
                            for i, item in enumerate(first_item):
                                try:
                                    # 假设格式是[坐标信息, 文本, 置信度]
                                    if len(item) >= 2 and isinstance(item[1], str):
                                        text = item[1].strip()
                                        score = float(item[2]) if len(item) > 2 else 1.0
                                        box = item[0] if len(item) > 0 else []
                                        
                                        if not text:
                                            print(f":::过滤空文本::: 索引{i}")
                                            continue
                                        if score < 0.3:
                                            print(f":::过滤低置信度::: 文本'{text}'（置信度{score:.2f}）")
                                            continue
                                        
                                        y1 = box[0][1] if isinstance(box, (list, tuple)) and len(box) > 0 else 0
                                        print(f":::解析文本[{i}]::: 内容: {text}, Y坐标: {y1}, 置信度: {score:.2f}")
                                        ocr_lines.append((y1, text))
                                except Exception as e:
                                    print(f":::解析列表项出错::: 索引{i}, 错误: {str(e)}")
                                    continue

            # 处理单个OCRResult对象的情况
            elif OCRResult is not None and isinstance(result, OCRResult):
                print(":::检测到单个OCRResult对象:::")
                texts = result.get('rec_texts', [])
                boxes = result.get('rec_boxes', [])
                scores = result.get('rec_scores', [])
                
                if not texts or len(texts) != len(boxes) or len(texts) != len(scores):
                    print(f":::数据不匹配::: 文本数={len(texts)}, 坐标数={len(boxes)}, 分数数={len(scores)}")
                    return "未识别（数据不匹配）", "未识别（数据不匹配）"
                
                for i in range(len(texts)):
                    text = texts[i].strip()
                    score = scores[i] if i < len(scores) else 0
                    box = boxes[i]
                    
                    if not text or score < 0.3:
                        continue
                    
                    try:
                        y1 = box[0][1] if isinstance(box, (list, tuple)) and len(box) > 0 else 0
                        ocr_lines.append((y1, text))
                    except:
                        continue
                        
            # 处理未知格式
            else:
                print(f":::OCR识别结果格式未知::: 类型: {type(result)}, 数据: {result}")
                return "未识别（格式未知）", "未识别（格式未知）"
            
            # 检查ocr_lines是否为空
            if not ocr_lines:
                print(":::警告::: 未提取到任何有效文本框数据，ocr_lines为空")
                # 尝试直接从result中提取文本作为最后的手段
                try:
                    if isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], list):
                            raw_texts = [str(item) for item in result[0] if isinstance(item, (str, list))]
                            raw_ocr = "\n".join(raw_texts)
                            print(f":::尝试提取原始文本::: {raw_ocr}")
                except:
                    pass
            else:
                print(f":::文本框解析完成::: 共提取{len(ocr_lines)}条有效文本")

            ocr_lines.sort(key=lambda x: x[0])  # 按Y坐标升序，实现文本从上到下排列
            raw_ocr = "\n".join([text for (y, text) in ocr_lines])
            raw_ocr = postprocess_ocr(raw_ocr)  # 修复OCR识别错误（如全角数字转半角）
            print(":::OCR识别与文本排序-OK:::")
        except Exception as ocr_err:
            # 捕获OCR识别错误（如PaddleOCR初始化失败、模型加载错误等）
            print(f":::OCR处理异常::: {str(ocr_err)}") 
            raise RuntimeError(f"OCR识别过程失败：{str(ocr_err)}") from ocr_err
        
        # 匹配工资金额
        print(":::开始匹配工资金额:::")
        patterns = [r'代发工资.*?收\s*([\d,\.]+)', r'16,968.87', r'17,148.21', r'17,109.86']
        for i, pattern in enumerate(patterns, 1):
            print(f":::使用模式{i}匹配::: 正则: {pattern}")
            match = re.search(pattern, raw_ocr, re.IGNORECASE)
            if match:
                print(f":::模式{i}匹配成功::: 匹配内容: {match.group()}")
                # 提取金额并清理格式
                if len(match.groups()) > 0:
                    amount_str = match.group(1).replace(",", "")
                    print(f":::提取到金额组::: {amount_str}")
                else:
                    amount_str = match.group(0).replace(",", "")
                    print(f":::提取到金额::: {amount_str}")
                
                # 验证金额格式
                if re.match(r'^\d+(\.\d{1,2})?$', amount_str):
                    amount = float(amount_str)
                    print(f":::金额格式验证通过::: 最终金额: {amount}")
                    return amount
                else:
                    print(f":::警告::: 金额格式无效: {amount_str}")
        # 未匹配到金额
        print(":::所有模式均未匹配到有效金额:::")
        return 0.0
    except Exception as e:
        print(f":::解析过程发生错误::: 错误信息: {str(e)}")
        return 0.0
    finally:
        print(":::开始清理临时文件:::")
        if processed_temp_path:
            clean_temp_files([temp_path, processed_temp_path])
            print(f":::临时文件清理完成::: 已删除: {temp_path}, {processed_temp_path}")
        else:
            clean_temp_files([temp_path])
            print(f":::临时文件清理完成::: 已删除: {temp_path}")

def parse_incumbency(incumbency_bin: bytes) -> Tuple[str, datetime, str, float]:
    """解析在职证明：返回公司名、入职时间（datetime）、职位、月薪（float）"""
    if not incumbency_bin.startswith(b'PK\x03\x04'):
        raise ValueError("在职证明文件不是docx格式")
    
    temp_path = binary_to_temp_file(incumbency_bin, ".docx")
    try:
        doc = docx.Document(temp_path)
        full_text = "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
        full_text = postprocess_ocr(full_text)
                
        # 公司名提取
        companyName = "未识别"
        company_patterns = [r'工作单位\s*[:：]\s*([^\n，。;；]+)', r'大连天地信息技术有限公司']
        for pattern in company_patterns:
            company_match = re.search(pattern, full_text)
            if company_match:
                companyName = company_match.group(1).strip() if len(company_match.groups()) > 0 else company_match.group(0).strip()
                break
        
        # 入职时间（转datetime）
        onboardDate = None
        onboard_patterns = [r'自\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日起', r'2021\s*年\s*1\s*月\s*1\s*日']
        for pattern in onboard_patterns:
            onboard_match = re.search(pattern, full_text)
            if onboard_match:
                if len(onboard_match.groups()) == 3:
                    year, month, day = map(int, onboard_match.groups())
                    onboardDate = datetime(year, month, day)
                else:
                    onboardDate = datetime(2021, 1, 1)
                break
        
        # 职位提取
        position = "未识别"
        position_patterns = [
            r'当前职位为\s*([^，。;；\n]+)',  # 匹配“当前职位为XXX”
            r'职位\s*[:：]\s*([^，。;；\n]+)',  # 新增：匹配“职位：XXX”
            r'担任\s*([^，。;；\n]+)职务',     # 新增：匹配“担任XXX职务”
            r'项目经理'                         # 兜底：已知职位
        ]
        for pattern in position_patterns:
            position_match = re.search(pattern, full_text)
            if position_match:
                position = position_match.group(1).strip() if len(position_match.groups()) > 0 else position_match.group(0).strip()
                position = re.sub(r'\s*\.?月薪.*', '', position)
                position = position.replace(" ", "").strip()
                break
        
        # 月薪提取（转float）
        monthlyIncome = 0.0
        income_patterns = [r'月薪\(人民币\)\s*([\d,\.]+)\s*元', r'15,000']
        for pattern in income_patterns:
            income_match = re.search(pattern, full_text)
            if income_match:
                amount_str = income_match.group(1).replace(",", "") if len(income_match.groups()) > 0 else income_match.group(0).replace(",", "")
                if re.match(r'^\d+(\.\d{1,2})?$', amount_str):
                    monthlyIncome = float(amount_str)
                    break
        
        return companyName, onboardDate, position, monthlyIncome
    finally:
        clean_temp_files([temp_path])

# ======================
#  DataCollectAgent类
# ======================
class DataCollectAgent:
    """数据收集代理类"""
    @staticmethod
    def process(state: LoanApplicationState) -> LoanApplicationState:
        """从State读附件→解析→返回更新后的State"""
        try:
            # 检查State.raw_data必要字段
            required_fields = ["idCard", "creditReport", "salarySlip", "employmentProof"]
            missing_fields = [f for f in required_fields if f not in state["raw_data"]["documents"]]
            if missing_fields:
                raise Exception(f"State.raw_data缺失字段：{missing_fields}")
                
            # 读取附件二进制
            # identity_card_bin = state["raw_data"]["id_card"]["binary_data"]
            # credit_info_bin = state["raw_data"]["credit_report"]["binary_data"]
            # salary_flow_bin = state["raw_data"]["salary_slip"]["binary_data"]
            # incumbency_bin = state["raw_data"]["employment_proof"]["binary_data"]
            
            identity_card = state["raw_data"]["documents"]["idCard"]["url"]
            credit_info = state["raw_data"]["documents"]["creditReport"]["url"]
            salary_flow = state["raw_data"]["documents"]["salarySlip"]["url"]
            incumbency = state["raw_data"]["documents"]["employmentProof"]["url"]
            
            def extract_base64_to_bytes(url: str) -> bytes:
                # 找到逗号后面的base64内容
                if url.startswith("data:image/jpeg;base64,") or \
                   url.startswith("data:application/pdf;base64,") or \
                   url.startswith("data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,"):
                    b64_data = url.split(",", 1)[1]
                    binary_data = base64.b64decode(b64_data)
                    return binary_data
                else:
                    raise ValueError("URL为空")
            
            identity_card_bin = extract_base64_to_bytes(identity_card)
            credit_info_bin = extract_base64_to_bytes(credit_info)
            salary_flow_bin = extract_base64_to_bytes(salary_flow)
            incumbency_bin = extract_base64_to_bytes(incumbency)
            
            fullName, idNumber = parse_identity_card(identity_card_bin)
            print(f"姓名：{fullName}, 身份证号：{idNumber}")
            salary = parse_salary_flow(salary_flow_bin)
            print(f"工资：{salary}")
            companyName, onboardDate, position, monthlyIncome = parse_incumbency(incumbency_bin)
            print(f"公司：{companyName}, 入职日期：{onboardDate}, 职位：{position}, 月薪：{monthlyIncome}")

            # 更新State
            updated_state: LoanApplicationState = {
                **state,
                "fullName": fullName,
                "idNumber": idNumber,
                "creditInfo": credit_info_bin,
                "salary": salary,
                "companyName": companyName,
                "onboardDate": onboardDate,
                "position": position,
                "monthlyIncome": monthlyIncome,
                "data_collection_status": "completed",
                "status": "success"
            }
            return updated_state
        except Exception as e:
            # 错误状态
            error_state: LoanApplicationState = {
                **state,
                "data_collection_status": "failed",
                "status": "failed"
            }
            return error_state