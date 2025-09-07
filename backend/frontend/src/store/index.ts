import { create } from 'zustand';
import type { Customer, ChatMessage } from '../types';

interface StoreState {
  // 客户相关状态
  customers: Customer[];
  setCustomers: (customers: Customer[]) => void;
  selectedCustomer: Customer | null;
  setSelectedCustomer: (customer: Customer | null) => void;
  selectedCustomerIds: string[];
  toggleCustomerSelection: (id: string) => void;
  clearCustomerSelections: () => void;
  
  // 弹窗状态
  isDetailDialogOpen: boolean;
  setIsDetailDialogOpen: (open: boolean) => void;
  
  // 聊天机器人状态
  chatMessages: ChatMessage[];
  addChatMessage: (message: ChatMessage) => void;
  clearChatMessages: () => void;
}

export const useStore = create<StoreState>((set, get) => ({
  // 客户相关
  customers: [],
  setCustomers: (customers) => set({ customers }),
  selectedCustomer: null,
  setSelectedCustomer: (customer) => set({ selectedCustomer: customer }),
  selectedCustomerIds: [],
  toggleCustomerSelection: (id) => {
    const { selectedCustomerIds } = get();
    if (selectedCustomerIds.includes(id)) {
      set({
        selectedCustomerIds: selectedCustomerIds.filter(customerId => customerId !== id)
      });
    } else {
      set({
        selectedCustomerIds: [...selectedCustomerIds, id]
      });
    }
  },
  clearCustomerSelections: () => set({ selectedCustomerIds: [] }),
  
  // 弹窗状态
  isDetailDialogOpen: false,
  setIsDetailDialogOpen: (open) => set({ isDetailDialogOpen: open }),
  
  // 聊天机器人
  chatMessages: [],
  addChatMessage: (message) => {
    const { chatMessages } = get();
    set({ chatMessages: [...chatMessages, message] });
  },
  clearChatMessages: () => set({ chatMessages: [] })
}));