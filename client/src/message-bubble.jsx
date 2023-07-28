import "./style/message-bubble.scss";
import { Box, IconButton, Icon, Tooltip } from '@mui/material';
import { copy } from 'clipboard';
import CopyIcon from '@mui/icons-material/FileCopy';
import ResetIcon from '@mui/icons-material/RestartAlt';
import ThumbsUpIcon from '@mui/icons-material/ThumbUp';
import ThumbsDownIcon from '@mui/icons-material/ThumbDown';
import ReactMarkdown from 'react-markdown';

// React function component for a message bubble
// Props: message, sender, time
// Returns: a message bubble
function MessageBubble(props) {
    // Copies a message to the clipboard
    const copyMessage = (content) => {
        copy(content);
    };

    return (
        <Box
            className={`message ${props.role} temperature-${props.temperature ?? 0} ${props.isHovered ? "with-menu" : ""}`}
            >
            { props.buttonBar &&
            (<Box
                className={`buttons-container ${props.role} ${props.isHovered ? "show" : ""}`}>
                {(props.role === 'system') || (props.role === 'user') ? (
                <>
                    <Tooltip title={<span className="tooltip">Copy to clipboard</span>} placement="top">
                        <IconButton  size="small" onClick={() => {copyMessage(props.content); props.setNotice("Text copied to clipboard");}}>
                            <span className="icon"><CopyIcon /></span>
                        </IconButton>
                    </Tooltip>

                    { !props.resetDisabled &&
                        <Tooltip title={<span className="tooltip">Reset to this message</span>} placement="top">
                            <IconButton size="small" onClick={() => {props.resetMessages(); props.setNotice("Conversation rewinded to an earlier point");}} disabled={props.resetDisabled}>
                                <span className="icon"><ResetIcon /></span>
                            </IconButton>
                        </Tooltip>}
                </>)
            : null}
            </Box>
            )}
            {props.source_documents && 
                <Box className="source-documents">
                    <h3>Source documents</h3>
                    {props.source_documents.map((doc, index) =>
                        <Box key={index} className="source-document">
                            <div className="content">{doc["page_content"]}</div>
                            <div className="metadata">{JSON.stringify(doc["metadata"])}</div>
                        </Box>)}
                </Box>}
            {props.thought && <ReactMarkdown className="thought" children={props.thought} />}
            {props.params &&
                <Box className="params">
                    <Box className="params">
                        {JSON.stringify(props.params)}
                    </Box>
                </Box>}
            {props.content && <ReactMarkdown className="inner-text" children={props.content} />}
        </Box>
    );
}

export default MessageBubble;
