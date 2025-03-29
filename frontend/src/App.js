import React, { useState } from 'react';
import './App.css';

function App() {
  // State variables to manage form inputs and cover letter generation
  const [letterStyle, setLetterStyle] = useState('modern');
  const [resume, setResume] = useState(null);
  const [jobURL, setJobURL] = useState('');
  const [extraDetails, setExtraDetails] = useState('');
  const [coverLetter, setCoverLetter] = useState('');
  const [loading, setLoading] = useState(false);
  const [comments, setComments] = useState('');

  // Handle file upload
  const handleResumeChange = (event) => {
    setResume(event.target.files[0]);
  };

  // Handle form submission to generate/re-generate the cover letter
  const handleSubmit = async (event, regenerate = false) => {
    event.preventDefault();

    if (!resume || !jobURL) {
      alert('Please upload a resume and enter a job name.');
      return;
    }

    setLoading(true);
    // Create a FormData object to send the file and other data
    const formData = new FormData();
    formData.append('resume', resume);
    formData.append('jobName', jobURL);
    formData.append('extraDetails', extraDetails);
    formData.append('letterStyle', letterStyle); // Send the chosen style

    // Append comments if re-generating
    if (regenerate && comments) {
      formData.append('comments', comments);
    }

    // Send the form data to the backend for processing
    try {
      const response = await fetch('http://localhost:5000/generate-cover-letter', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setCoverLetter(data.coverLetter);
    } catch (error) {
      console.error('Error generating cover letter:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle download of the cover letter PDF compiled from LaTeX on the backend
  const handleDownload = async () => {
    try {
      const response = await fetch('http://localhost:5000/compile-latex', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ latex: coverLetter })
      });
      if (!response.ok) {
        throw new Error('Compilation failed');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = 'cover-letter.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error compiling PDF:', error);
    }
  };
  

  return (
    <div className="container">
      {/* Header and title */}
      <h2>Cover Letter Generator</h2>
      <form onSubmit={handleSubmit}>
        {/* File input for resume upload */}
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleResumeChange}
          required
        />
        {/* Text input for job URL */}
        <input
          type="text"
          placeholder="Enter Job URL"
          value={jobURL}
          onChange={(e) => setJobURL(e.target.value)}
          required
        />
        {/* Text input for extra details */}
        <input
          type="text"
          placeholder="Enter any extra details you wish to add"
          value={extraDetails}
          onChange={(e) => setExtraDetails(e.target.value)}
          required
        />
        {/* Dropdown for selecting cover letter structure */}
        <label htmlFor="letterStyle"><strong>Select Cover Letter Structure</strong></label>
        <select
          id="letterStyle"
          value={letterStyle}
          onChange={(e) => setLetterStyle(e.target.value)}
        >
          <option value="modern">Modern</option>
          <option value="traditional">Traditional</option>
          <option value="creative">Creative</option>
        </select>

        {/* Submit button to generate cover letter */}
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Cover Letter'}
        </button>
      </form>

      {/* Display the generated cover letter if available */}
      {coverLetter && (
        <div className="cover-letter-container">
          <h2>Generated Cover Letter (Raw LaTeX)</h2>
          <textarea
            value={coverLetter}
            onChange={(e) => setCoverLetter(e.target.value)}
          />
          <button onClick={handleDownload}>Download PDF</button>

          <div className="comment-box">
            <label htmlFor="comments">
              <strong>Suggest Edits for Re-generation</strong>
            </label>
            <textarea
              id="comments"
              placeholder="Add your comments here..."
              value={comments}
              onChange={(e) => setComments(e.target.value)}
            />
            <button onClick={(e) => handleSubmit(e, true)}>
              Re-generate with Comments
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
