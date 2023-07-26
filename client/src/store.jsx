import {create} from 'zustand';
import { v4 as uuidv4 } from 'uuid';

const WELCOME_MESSAGE = "Hi, I am a chatbot with access to lectures and reading materials. I can help you explore themes in microeconomics.";

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
    TESTING: false,
    resetMessages: (_init) => {
        console.log("once more")
        if (_init) {
            console.log("here");
            set({messages: []});
        }
        else {
            set(state => state.TESTING ? {messages: [
                {"content": WELCOME_MESSAGE, "role" : "system"},
                {"content": WELCOME_MESSAGE, "role" : "user"},
                {"content": WELCOME_MESSAGE, "role" : "system"},
            ]} : {messages: [
                    {"content": WELCOME_MESSAGE, "role" : "system"},
            ]});
        }
      }
}));

export default useStore;
