import React, { useRef, useState, useEffect, useImperativeHandle, forwardRef } from "react";
import { Typography, Button, Box, CircularProgress, Tooltip } from '@mui/material';
import TextareaAutosize from "react-textarea-autosize";
import MessageBubble from "./message-bubble";
import ButtonBar from "./button-bar";
import ReactMarkdown from 'react-markdown';
import useStore from "./store";
import uuid4 from "uuid";
import "./style/chat.scss";
import Notice from "./notice"

const TESTING = false;

function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value; //assign the value of ref to the argument
  },[value]); //this code will run when the value of 'value' changes
  return ref.current; //in the end, return the current ref value.
}

const Chat = React.forwardRef((props, ref) => {
  const WELCOME_MESSAGE = "Hi, I am a chatbot with access to lectures and reading materials. I can help you explore themes in microeconomics.";
  const messagesEndRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [isInMenuHovered, setIsInMenuHovered] = useState(false);
  const [text, setText] = useState("");
  const [timeoutId, setTimeoutId] = useState(-1);
  const [interrupted, setInterrupted] = useState(false);
  const [isInit, setIsInit] = useState(true);
  const textareaRef = useRef(null);
  const abortController = useRef(null);
  const submitButtonRef = useRef(null);
  const chatFont = "'Bitter', serif";
  const PrevIsInMenuHovered = usePrevious(isInMenuHovered);

  const setNotice = useStore(state => state.setNotice);
  const temperature = useStore(state => state.temperature);
  const chatId = useStore(state => state.chatId);
  const setChatId = useStore(state => state.setChatId);
  const genChatId = useStore(state => state.genChatId);
  const incoming = useStore(state => state.incoming);
  const setIncoming = useStore(state => state.setIncoming);
  const messages = useStore(state => state.messages);
  const setMessages = useStore(state => state.setMessages);
  const appendMessage = useStore(state => state.appendMessage);

  useEffect(() => {
    genChatId();
  }, [genChatId]);

  const hovered = (value, location) => {
    setIsHovered(value);
  };

  const menu_hovered = (value, location) => {
    setIsInMenuHovered(value);
  };

  const createHoverTimeout = () => {
    if (timeoutId !== -1) {
      clearTimeout(timeoutId);
    }
    const _t = setTimeout(() => { hovered(false, 1); }, 2000);
    setTimeoutId(_t);
  }

  // Clears timer for hover
  const resetHoverTimeout = () => {
    if (timeoutId !== -1) {
      clearTimeout(timeoutId);
      setTimeoutId(-1);
    }
  }

  // On submit, add message and clear output
  const handleSubmit = () => {
    if (text.trim()) {
      hovered(false, 2);
      newMessage(text, 'user')
      setText("");
    }
  };

  // On keydown, if enter is pressed, submit the message
  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
    hovered(false, 3);
  };

  // Global initialization, installs body event listeners
  useEffect(() => {
    let lastOpened = 0;
    resetChat(isInit);
    document.documentElement.style.setProperty('--body-font', chatFont);

    const handleMouseEnter = () => {
      if (Date.now() - lastOpened > 5000) {
        lastOpened = Date.now();
        hovered(true, 4);
      }
    };

    const handleMouseLeave = () => {
      lastOpened = 0;
    };
    document.body.addEventListener('mousemove', handleMouseEnter);
    document.body.addEventListener('mouseleave', handleMouseLeave);

    setFocusInput();
    hovered(false, 5);
    if (TESTING) {
      // Disables boot for testing
      setIsLoading(false);
      setIsInit(false);
      resetChat(false);
    }
    else {
      // Normal boot sequence
      setIsLoading(true);
      setTimeout(() => initialAnimation(), 200);
    }

    return () => {
      document.body.removeEventListener('mousemove', handleMouseEnter);
      document.body.removeEventListener('mouseleave', handleMouseEnter);
    };
  }, []);

  const initialAnimation = () => {
    const welcome = WELCOME_MESSAGE;
    animate (welcome, () => {
      setIncoming("");
      setIsInit(false);
      resetChat(false);
      setIsLoading(false);
      setFocusInput();
    });
  };

  const animate = (text, cleanup) => {
    let speaking = "";
    const f = (words) => {
      setTimeout(() => {
        if (words.length > 0) {
          speaking = speaking + " " + words.shift();
          setIncoming(speaking + "\u258C");
          f(words);
        }
        else {
          cleanup();
        }
      }, 100);
    }
    setTimeout(() => {
      const words = text.split(" ");
      const parts = [];
      while (words.length > 0) {
        const j = [];
        for(let i = 0; i < 3; i++) {
          if (words.length > 0)
            j.push(words.shift());
        }
        parts.push(j.join(" "));
      }
      f(parts);
    }, 500);
  };

  // When hover begins, sets a timer to unset it in 2 seconds
  useEffect(() => {
    if (!isInit) {
      resetHoverTimeout();
      if (isHovered) {
        createHoverTimeout();
      }
    }
    else
      hovered(false, 6);
  }, [isHovered]);

  useEffect((prevValue) => {
    if (isInMenuHovered) {
      hovered(true, 7);
      resetHoverTimeout();
    }
    else
      if (PrevIsInMenuHovered) {
        createHoverTimeout();
      }
  }, [isInMenuHovered]);

  // After loading, sets focus to the textarea
  useEffect(() => {
    if (!isLoading)
      setFocusInput();
  }, [isLoading]);

  const stopFetching = () => {
    if (abortController.current) {
      abortController.current.abort();
    }
    setInterrupted(true);
  };

  // On Change for messages and temperature
  // Send a POST request to the API and animates streaming response
  useEffect(() => {
    abortController.current = new AbortController();
    const signal = abortController.signal;

    const fetchChat = async () => {
      setIncoming("\u258C")
      setIsLoading(true);
      scrollToBottom();
      const response = await fetch("/api/chat", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({chatId, chat: messages.slice(1), temperature}),
        signal: signal
      });

      let completeResponse = "";
      const decoder = new TextDecoder('utf-8');
      const processTimeout = setTimeout(() => { console.warn("Interrupted receiving process due to timeout"); setInterrupted(true);}, 90000);

      let incoming_content = "";
      setInterrupted(false);
      async function processResponse() {
        let reader = response.body.getReader();

        while (!interrupted) {
            const { done, value: chunk } = await reader.read();
            if (done) { break; }

            let chunk_str = decoder.decode(chunk);
            let doneIndex = chunk_str.indexOf('\n\n**DONE**');

            if (doneIndex !== -1) {
                let doneChunk = chunk_str.substring(doneIndex, chunk_str.length);
                const json_str = doneChunk.replace('**DONE**\n\n', '');
                chunk_str = chunk_str.substring(0, doneIndex);
            }
            incoming_content += chunk_str;
            setIncoming(incoming_content + "\u258C");
            scrollToBottom();
        }
        clearTimeout(processTimeout);
        appendMessage({ content: incoming_content, role: "system", temperature });
        setIsLoading(false);
      }

      processResponse();
    };

    if (messages.length > 0 && messages[messages.length - 1].role === "user") {
      fetchChat();
    }

    return () => {
      abortController.current.abort(); // abort fetch on component unmount or when useEffect dependencies change
    };
  }, [messages, temperature]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, text]);

  // Adds a new message to the messages array
  const newMessage = async (text, role) => {
    appendMessage({ content: text, role: role })
  };

  // Sets focus to textarea
  const setFocusInput = (text) => {
    if (text)
      setText(text);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }

  // Resets the chat
  const resetChat = (_init) => {
    if (_init) {
      setMessages([]);
    }
    else {
      if (TESTING)
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
  };

  // Loads chat into the window
  const loadChat = (chat) => {
    genChatId();
    setMessages([{"content": WELCOME_MESSAGE, "role" : "system"}, ...chat.messages]);
  }

  // Clears messages up to the given index
  const resetMessages = (index, submit=false) => {
    let text = null;
    if (!submit && messages[index].role === 'user') {
      text = messages[index].content;
      index--;
    }
    setMessages(messages.slice(0, index + 1));
    setFocusInput(text ?? "");
  };

  // Scrolls screen to bottom
  const scrollToBottom = () => {
    textareaRef.current?.focus();
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Handles menu shortcuts
  const handleMenuShortcut = (e, index) => {
    switch(index) {
      case 0: stopFetching(); break;
      case 1:
        if (messages.length > 1)
          resetMessages(messages.length - 2, submit=true);
        break;
      case 2: resetChat(isInit); break;
    }
    e.stopPropagation();
  };

  const handleBackgroundClick = (e) => {
    menu_hovered(false, 8);
    hovered(false, 9);
  };

  return (
    <>
    <Box className="chat"
        onMouseLeave={() => hovered(false)}
        onClick={handleBackgroundClick}>

        {messages.map(({ content, role, temperature }, index) =>
            <MessageBubble key={index}
                content={content}
                role={role}
                temperature={temperature}
                isHovered={isHovered}
                setHovered={(v) => menu_hovered(v, 467)}
                buttonBar={index > 0}
                setNotice={setNotice}
                resetDisabled={index === messages.length - 1}
                resetMessages={() => resetMessages(index)} />)}

        {!isLoading &&
            (<>
                <TextareaAutosize
                  className="user-input"
                  placeholder="Type here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  ref={textareaRef}
                  style={{fontFamily: chatFont}}
                  rows={1}
                />

                <Box className="submit" style={{textAlign: 'center'}} ref={submitButtonRef}>
                    <Button
                    className="submit-button"
                    onClick={handleSubmit}>
                        Submit
                    </Button>
                </Box>
            </>)
        }

        {isLoading &&
          <>
            <Box className={`message system temperature-0`} sx={{ marginTop: 0, paddingTop: 0 }}>
                <ReactMarkdown className="inner-text" children={incoming} />
            </Box>
            <Box display="flex" justifyContent="center" mt={2} className="hourglass">
                <CircularProgress size={"1em"} />
            </Box>
          </>}

        <ButtonBar isHovered={isHovered} setHovered={(v) => menu_hovered(v, 402)} handleClick={handleMenuShortcut} />
    </Box>
    <div ref={messagesEndRef} />
    <Notice / >
    </>
  );
});

export default Chat;
