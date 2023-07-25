import React from "react";
import { Box, Typography, Button, Grid } from "@mui/material";
import "./style/ShortcutButton.scss";

const ShortcutButton = ({ index, caption, onClick, onFocus }) => (
    <Grid item xs={4}>
    <Button
      onClick={onClick}
      onFocus={onFocus}
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "8em", // specify the width
        height: "8em", // specify the height
        opacity: 0.8,
      }}
    >
        <Box className={`icon icon-00${index+1}`}></Box>
        <Typography variant="caption" className="label"  sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '30px', // fixed height
          lineHeight: '20px', // adjust this to change the spacing between lines
          textAlign: 'center',
          fontSize: '1em',
        }}>
                {caption}
        </Typography>
      </Button>
    </Grid>
);

export default ShortcutButton;
