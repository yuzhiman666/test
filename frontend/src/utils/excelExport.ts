import * as XLSX from 'xlsx';

interface ColumnConfig<T> {
  header: string;
  key: keyof T | ((row: T) => any);
  width?: number;
  formatter?: (value: any) => string;
}

interface ExportOptions<T> {
  filename?: string;
  sheetName?: string;
  columns: ColumnConfig<T>[];
  data: T[];
  autoWidth?: boolean;
  beforeExport?: (data: T[]) => T[];
}

/**
 * 将数据转换为适合Excel导出的格式
 */
const prepareExportData = <T>(data: T[], columns: ColumnConfig<T>[]): any[][] => {
  // 创建表头
  const headerRow = columns.map(col => col.header);
  
  // 创建数据行
  const dataRows = data.map(row => {
    return columns.map(col => {
      // 获取原始值
      let value;
      if (typeof col.key === 'function') {
        value = col.key(row);
      } else {
        value = row[col.key];
      }
      
      // 应用格式化器
      if (col.formatter) {
        return col.formatter(value);
      }
      
      // 处理特殊值
      if (value === null || value === undefined) {
        return '';
      }
      
      // 处理日期
      if (value instanceof Date) {
        return value.toISOString().split('T')[0];
      }
      
      return value;
    });
  });
  
  return [headerRow, ...dataRows];
};

/**
 * 导出数据到Excel文件
 * @param options 导出配置
 */
const exportToExcel = <T>(options: ExportOptions<T>): void => {
  try {
    const {
      filename = 'export',
      sheetName = 'Sheet1',
      columns,
      data,
      autoWidth = true,
      beforeExport,
    } = options;
    
    // 处理数据（可选）
    let exportData = [...data];
    if (beforeExport) {
      exportData = beforeExport(exportData);
    }
    
    // 准备导出数据
    const exportRows = prepareExportData(exportData, columns);
    
    // 创建工作簿和工作表
    const worksheet = XLSX.utils.aoa_to_sheet(exportRows);
    
    // 设置列宽
    if (autoWidth) {
      worksheet['!cols'] = columns.map(col => ({
        wch: col.width || 15 // 默认宽度
      }));
    }
    
    // 创建工作簿并添加工作表
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
    
    // 生成文件名（确保有.xlsx扩展名）
    const fileNameWithExt = filename.endsWith('.xlsx') ? filename : `${filename}.xlsx`;
    
    // 导出文件
    XLSX.writeFile(workbook, fileNameWithExt);
    
  } catch (error) {
    console.error('Excel export failed:', error);
    throw new Error('Failed to export data to Excel. Please try again.');
  }
};

/**
 * 导出多个工作表到一个Excel文件
 */
const exportMultipleSheetsToExcel = <T>({
  filename = 'export',
  sheets,
}: {
  filename?: string;
  sheets: Array<{
    sheetName: string;
    columns: ColumnConfig<T>[];
    data: T[];
    autoWidth?: boolean;
    beforeExport?: (data: T[]) => T[];
  }>;
}): void => {
  try {
    const workbook = XLSX.utils.book_new();
    
    sheets.forEach((sheet) => {
      const {
        sheetName,
        columns,
        data,
        autoWidth = true,
        beforeExport,
      } = sheet;
      
      // 处理数据（可选）
      let exportData = [...data];
      if (beforeExport) {
        exportData = beforeExport(exportData);
      }
      
      // 准备导出数据
      const exportRows = prepareExportData(exportData, columns);
      
      // 创建工作表
      const worksheet = XLSX.utils.aoa_to_sheet(exportRows);
      
      // 设置列宽
      if (autoWidth) {
        worksheet['!cols'] = columns.map(col => ({
          wch: col.width || 15
        }));
      }
      
      // 添加到工作簿
      XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
    });
    
    // 生成文件名
    const fileNameWithExt = filename.endsWith('.xlsx') ? filename : `${filename}.xlsx`;
    
    // 导出文件
    XLSX.writeFile(workbook, fileNameWithExt);
    
  } catch (error) {
    console.error('Multiple sheets Excel export failed:', error);
    throw new Error('Failed to export data to Excel. Please try again.');
  }
};

export { exportToExcel, exportMultipleSheetsToExcel };
export type { ColumnConfig, ExportOptions };