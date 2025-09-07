import { useState, useEffect, useCallback } from 'react';

interface PaginationOptions {
  initialPage?: number;
  pageSize?: number;
  totalItems?: number;
}

interface PaginationResult {
  currentPage: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  setCurrentPage: (page: number) => void;
  setPageSize: (size: number) => void;
  setTotalItems: (total: number) => void; // 新增：允许外部更新总条数
  nextPage: () => void;
  prevPage: () => void;
  hasNextPage: boolean;
  hasPrevPage: boolean;
  startIndex: number;
  endIndex: number;
  resetPagination: () => void;
}

/**
 * 分页逻辑自定义Hook
 * @param options 分页初始配置
 * @returns 分页相关状态和操作方法
 */
const usePagination = ({
  initialPage = 1,
  pageSize = 10,
  totalItems = 0,
}: PaginationOptions = {}): PaginationResult => {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSizeState, setPageSizeState] = useState(pageSize);
  const [totalItemsState, setTotalItemsState] = useState(totalItems);

  // 计算总页数
  const totalPages = Math.max(Math.ceil(totalItemsState / pageSizeState), 1);

  // 检查是否有上一页/下一页
  const hasNextPage = currentPage < totalPages;
  const hasPrevPage = currentPage > 1;

  // 计算当前页的起始和结束索引
  const startIndex = (currentPage - 1) * pageSizeState;
  const endIndex = Math.min(startIndex + pageSizeState, totalItemsState);

  // 安全设置当前页（确保在有效范围内）
  const setSafeCurrentPage = useCallback((page: number) => {
    if (page < 1) {
      setCurrentPage(1);
    } else if (page > totalPages) {
      setCurrentPage(totalPages);
    } else {
      setCurrentPage(page);
    }
  }, [totalPages]);

  // 下一页
  const nextPage = useCallback(() => {
    if (hasNextPage) {
      setCurrentPage(prev => prev + 1);
    }
  }, [hasNextPage]);

  // 上一页
  const prevPage = useCallback(() => {
    if (hasPrevPage) {
      setCurrentPage(prev => prev - 1);
    }
  }, [hasPrevPage]);

  // 设置每页条数，重置到第一页
  const setPageSize = useCallback((size: number) => {
    setPageSizeState(size);
    setCurrentPage(1);
  }, []);

  // 新增：允许外部更新总条数
  const setTotalItems = useCallback((total: number) => {
    setTotalItemsState(total);
  }, []);

  // 更新总条数时，确保当前页有效
  useEffect(() => {
    setTotalItemsState(totalItems);
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalItems, totalPages, currentPage]);

  // 重置分页状态
  const resetPagination = useCallback(() => {
    setCurrentPage(initialPage);
    setPageSizeState(pageSize);
  }, [initialPage, pageSize]);

  return {
    currentPage,
    pageSize: pageSizeState,
    totalItems: totalItemsState,
    totalPages,
    setCurrentPage: setSafeCurrentPage,
    setPageSize,
    setTotalItems, // 暴露更新总条数的方法
    nextPage,
    prevPage,
    hasNextPage,
    hasPrevPage,
    startIndex,
    endIndex,
    resetPagination,
  };
};

export default usePagination;