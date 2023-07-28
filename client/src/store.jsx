import {create} from 'zustand';
import { v4 as uuidv4 } from 'uuid';


const useStore = create((set) => ({
    WELCOME_MESSAGE: "Hi, I am a chatbot with access to lectures and reading materials. I can help you explore themes in microeconomics. You can chat with me directly, or you can explore the question database on the top. \n\nPlease note this is experimental work, the author and owner of this website does not hold himself responsible for any errors in the answers.",
    chatId: null,
    genChatId: () => set(() => ({ chatId: uuidv4() })),
    setChatId: (chatId) => set({ chatId: chatId }),
    temperature: 0,
    setTemperature: (temperature) => set({ temperature: temperature }),
    text: "",
    setText: (text) => set({ text: text }),
    notice: "",
    setNotice: (notice) => set({ notice: notice }),
    incoming : "\u258C",
    setIncoming: (incoming) => set({ incoming: incoming }),
    messages: [],
    setMessages: (messages) => set({ messages: messages }),
    appendMessage: (message) => set({ messages: [...useStore.getState().messages, message] }),
    TESTING: false,
    resetMessages: (_init) => {
        if (_init) {
            set({messages: []});
        }
        else {
            set(state => state.TESTING ? {messages: [
                {"content": state.WELCOME_MESSAGE, "role" : "system"},
                {"content": state.WELCOME_MESSAGE, "role" : "user"},
                {"content": state.WELCOME_MESSAGE, "role" : "system"},
            ]} : {messages: [
                    {"content": state.WELCOME_MESSAGE, "role" : "system"},
            ]});
        }
      },
    questionData: null,
    setQuestionData: (question) => set({questionData: question}),
}));

export default useStore;
