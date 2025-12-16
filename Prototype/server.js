//NodeJS express Web server for prototype

//Import required modules
const express = require('express');
const fs = require('fs');
const { spawn } = require('child_process');
const path = require('path');
const { ok } = require('assert');

//Server configuration
const app = express();
const PORT = 3000;
const host = 'localhost';
app.use(express.json());

// audio file serving static directory
app.use('/audio', express.static('tts_out'));

// GET Root route: Serve index page
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

//post /generate route: run LLM - TTS pipeline
app.post("/generate", (req, res) => {
  const python_process = spawn("python", ["scripts/pipeline.py"]);

  let output_data = "";
  let error_data = "";

  python_process.stdout.on("data", (data) => {
    output_data += data.toString();
  });

  python_process.stderr.on("data", (data) => {
    error_data += data.toString();
  });

  python_process.on("close", (code) => {
    if (code !== 0) {
      console.error("Python returned error code:", code);
      console.error("Error returned from python:", error_data);
      return res.status(500).json({
        ok: false,
        error: "Python script failed",
        code,
        stderr: error_data.trim(),
      });
    }
    console.log("Python script output:", output_data);
    // Successful execution
    let parsedOutput;
    try {
      parsedOutput = JSON.parse(output_data);
    } catch (e) {
      console.error("Error parsing JSON:", e);
      return res.status(500).json({
        ok: false,
        error: "Error parsing JSON: " + e,
      });
    }

    //Everything successful (Python and JSON parsing), return to front end
    return res.json({
      ok: true,
      title: parsedOutput['title'],
      audioUrl: "/audio/final_podcast.mp3",
      downloadUrl: "/download/final_podcast.mp3",
      dialogue: parsedOutput['dialogue'],
    });
  });
});

// GET /download/:filename route: download podcast audio file
app.get("/download/:filename", (req, res) => {
  const filePath = path.join(__dirname, 'tts_out', req.params.filename);
  if (!fs.existsSync(filePath)) {
    return res.status(404).send("Podcast not found");
  }
  return res.download(filePath);
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
