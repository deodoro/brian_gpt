import React from 'react';
import { Button, Typography } from '@mui/material';

const FileUploader = ({ onFileChange, fileName, fileType }) => (
  <>
    <input
      accept={  fileType }
      style={{ display: 'none' }}
      id="contained-button-file"
      type="file"
      onChange={onFileChange}
    />
    <label htmlFor="contained-button-file">
      <Button variant="contained" component="span">
        Select File
      </Button>
    </label>
    {fileName && <Typography variant="subtitle1">{fileName}</Typography>}
  </>
);

export default FileUploader;
