import { Box } from '@mui/material';
import ShortcutButton from './ShortcutButton';
import "./style/button-bar.scss";

function ButtonBar(props) {
    const captions = ["Regenerate last reply",
                      "Begin New Chat",
                      "Chat Direction"];

    return (<Box className={`button-bar  ${props.isHovered ? "show" : ""}`}
                onMouseEnter={() => props.setHovered(true)}
                onMouseLeave={() => props.setHovered(false)}
            >
                {captions.map((item, index) => (
                    <ShortcutButton
                    key={index}
                    index={index}
                    caption={item}
                    onClick={(e) => props.handleClick(e, index)}
                    onFocus={() => props.setHovered(true) }
                    />
                ))}
            </Box>)
}

export default ButtonBar;
