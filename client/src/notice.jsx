import React, {useState, useEffect} from 'react';
import { Typography, Box } from '@mui/material';
import useStore from './store';

Notice = () => {
    const notice = useStore((state) => state.notice));
    const setNotice = useStore((state) => state.setNotice));
    const [noticeShow, setNoticeShow] = useState(false);
    const [lastNotice, setLastNotice] = useState("");

    useEffect(() => {
        if (notice) {
            setNoticeShow(true);
            setLastNotice(notice);
            setTimeout(() => {
                setNoticeShow(false);
                setNotice("");
            }, 2500);
        }
    }, [notice]);

    return (
        <Box className={`notice ${noticeShow ? "show": ""}`}>
            <Typography variant="h5" className="noticeText">
                <span>{lastNotice}</span>
            </Typography>
        </Box>
    );
}

export default Notice;
