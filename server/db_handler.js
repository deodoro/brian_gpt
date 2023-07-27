import express from 'express';
import pkg from 'pg';
const { Pool } = pkg;

const router = express.Router();

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_DATABASE,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  driver: process.env.DB_DRIVER
});

router.get('/years', async (req, res) => {
  const result = await pool.query('SELECT DISTINCT year FROM questions ORDER BY year');
  res.send(result.rows.map(row => row.year));
});

router.get('/exams/:year', async (req, res) => {
  const result = await pool.query('SELECT DISTINCT exam FROM questions WHERE year = $1 ORDER BY exam', [req.params.year]);
  res.send(result.rows.map(row => row.exam));
});

router.get('/parts/:year/:exam', async (req, res) => {
  const result = await pool.query('SELECT DISTINCT part FROM questions WHERE year = $1 AND exam = $2 ORDER BY part', [req.params.year, req.params.exam]);
  res.send(result.rows);
});

router.get('/numbers/:year/:exam/:part', async (req, res) => {
  const result = await pool.query('SELECT DISTINCT number FROM questions WHERE year = $1 AND exam = $2 AND part = $3 ORDER BY number', [req.params.year, req.params.exam, req.params.part]);
  res.send(result.rows);
});

router.get('/questions/:year', async (req, res) => {
    const result = await pool.query('SELECT addr, id FROM questions WHERE year = $1 ORDER BY part, number', [req.params.year]);
    res.send(result.rows);
  });

router.get('/questions/:year/:exam', async (req, res) => {
  const result = await pool.query('SELECT addr, id FROM questions WHERE year = $1 AND exam = $2 ORDER BY part, number', [req.params.year, req.params.exam]);
  res.send(result.rows);
});

router.get('/questions/:year/:exam/:part/:number', async (req, res) => {
  const result = await pool.query('SELECT * FROM questions WHERE year = $1 AND exam = $2 AND part = $3 AND number = $4', [req.params.year, req.params.exam, req.params.part, req.params.number]);
  res.send(result.rows);
});

router.get('/question/:id', async (req, res) => {
  const result = await pool.query('SELECT * FROM questions WHERE id = $1', [req.params.id]);
  if (result.rows.length === 0) {
    res.send({})
  }
  else {
    res.send(result.rows[0]);
  }
});

export default router;
