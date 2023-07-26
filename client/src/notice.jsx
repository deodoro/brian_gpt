import React, {useState, useEffect} from 'react';
import { Typography, Box } from '@mui/material';
import useStore from './store';

Notice = () => {
    const notice = useStore((state) => state.notice));
    const [noticeShow, setNoticeShow] = useState(false);

    useEffect(() => {
        if (notice) {
            setNoticeShow(true);
            setTimeout(() => {
            setNoticeShow(false);
            }, 2500);
        }
    }, [notice]);

    return (
        <Box className={`notice ${noticeShow ? "show": ""}`}>
            <Typography variant="h5" className="noticeText">
                <span>{notice}</span>
            </Typography>
        </Box>
    );
}

export default Notice;
