import create from 'zustand';
import { v4 as uuidv4 } from 'uuid';

const useStore = create((set) => ({
    chatId: null,
    genChatId: () => set(() => ({ chatId: uuidv4() })),
    setChatId: (chatId) => set({ chatId: chatId }),
    temperature: 0,
    setTemperature: (temperature) => set({ temperature: temperature }),
    notice: "",
    setNotice: (notice) => set({ notice: notice }),
    incoming : "\u258C",
    setIncoming: (incoming) => set({ incoming: incoming }),
    messages: [],
    setMessages: (messages) => set({ messages: messages }),
    appendMessage: (message) => set({ messages: [...useStore.getState().messages, message] }),
    TESTING: true,
    resetMessages: (_init) => {
        set(state => {
            if (_init) {
                setMessages([]);
              }
              else {
                if (state.TESTING)
                  setMessages([
                    {"content": WELCOME_MESSAGE, "role" : "system"},
                    {"content": WELCOME_MESSAGE, "role" : "user"},
                    {"content": WELCOME_MESSAGE, "role" : "system"},
                  ]);
                else
                  setMessages([
                    {"content": WELCOME_MESSAGE, "role" : "system"},
                  ]);
              }
        })
      }
}));

export default useStore;
