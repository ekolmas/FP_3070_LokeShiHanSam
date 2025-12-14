//Web server for prototype

//Running on port 3000
const express = require('express');
const {spawn} = require('child_process');
const app = express();
const PORT = 3000;
const host = 'localhost';

// Define a route for GET requests to the root URL
app.get('/', (req, res) => {
  res.send('Hello World from Express!');
});

// Route to test python NodeJS integration
app.get("/python_test/:testingParam", (req, res) => {
  const testingParam = req.params.testingParam;

  // spawn python process
  const pythonProcess = spawn("python", ["scripts/testing.py", testingParam]);

  let stdoutData = "";
  let stderrData = "";

  pythonProcess.stdout.on("data", (chunk) => {
    stdoutData += chunk.toString();
  });

  pythonProcess.stderr.on("data", (chunk) => {
    stderrData += chunk.toString();
  });

  pythonProcess.on("close", (code) => {
    if (code !== 0) {
      console.error("Python exited with code:", code);
      console.error("Python stderr:", stderrData.trim());
      return res.status(500).json({
        ok: false,
        error: "Python script failed",
        code,
        stderr: stderrData.trim(),
      });
    }

    const lines = stdoutData
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter(Boolean);

    const returnedValue = lines.length ? lines[lines.length - 1] : "";

    console.log(`NodeJS received the number ${returnedValue} from python`);

    //send to front end
    return res.json({
      ok: true,
      sentToPython: testingParam,
      receivedFromPython: returnedValue,
      pythonLogLines: lines,
    });
  });
});

// Start the server on port 3000
app.listen(PORT, host, () => {
  console.log(`Server running at http://${host}:${PORT}/`);
});
