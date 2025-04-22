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
  const [downloadLoading, setDownloadLoading] = useState(false);

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
      // console.log(data);
      setCoverLetter(data.coverLetter);
    } catch (error) {
      console.error('Error generating cover letter:', error);
    } finally {
      setLoading(false);

            // Scroll down to download
            console.log("Begin scrolling");
            setTimeout(function () {
              document.getElementById('pdfDownload').scrollIntoView({
                  behavior: "smooth",
                  block: "start",
              });
            }, 100);
    }
  };

  // Handle download of the cover letter PDF compiled from LaTeX on the backend
  const handleDownload = async () => {
    setDownloadLoading(true);
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
    } finally {
      setDownloadLoading(false);
    }
  };


  // Render the main UI component of the Cover Letter Generator app
  return (
    <div className="container">
      {/* Header and title of the application */}
      <h2>Cover Letter Generator</h2>
      
      {/* Form handles resume upload, entering job URL, extra details, and letter style */}
      <form onSubmit={handleSubmit}>
        {/* File input for uploading a resume document */}
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleResumeChange}
          required
        />
        
        {/* Text input for entering the job URL */}
        <input
          type="text"
          placeholder="Enter Job URL"
          value={jobURL}
          onChange={(e) => setJobURL(e.target.value)}
          required
        />
        
        {/* Text input for providing any extra details */}
        <input
          type="text"
          placeholder="Enter any extra details you wish to add"
          value={extraDetails}
          onChange={(e) => setExtraDetails(e.target.value)}
          required
        />
        
        {/* Dropdown menu for selecting the cover letter structure style */}
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

        {/* Submit button to generate cover letter with a spinner when loading */}
        <button type="submit" disabled={loading}>
          {loading && <div className="spinner"></div>}
          {loading ? 'Generating...' : 'Generate Cover Letter'}
        </button>
      </form>

      {/* Section to display the generated cover letter if available */}
      {coverLetter && (
        <div className="cover-letter-container" style={{
          marginTop: '50px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          width: '100%'
        }}>
          {/* Title for the generated cover letter */}
          <h2>Generated Cover Letter (Raw LaTeX)</h2>
          
          {/* Textarea to show the LaTeX code for the cover letter, editable for further modifications */}
          <textarea
            value={coverLetter}
            onChange={(e) => setCoverLetter(e.target.value)}
            style={{
              width: '90%',
              height: '500px',
              padding: '20px',
              marginBottom: '20px',
              fontSize: '16px',
              lineHeight: '1.5',
              fontFamily: 'monospace'
            }}
          />
          
          {/* Button to trigger PDF download, shows spinner during PDF creation */}
          <button id="pdfDownload"
            onClick={handleDownload} 
            disabled={downloadLoading}
            style={{ marginBottom: '30px' }}
          >
            {downloadLoading && <div className="spinner"></div>}
            {downloadLoading ? 'Creating PDF...' : 'Download PDF'}
          </button>

          {/* Section for suggesting edits when re-generating the cover letter */}
          <div className="comment-box" style={{ width: '90%' }}>
            {/* Label for the comments textarea */}
            <label htmlFor="comments">
              <strong>Suggest Edits for Re-generation</strong>
            </label>
            
            {/* Textarea for adding comments/suggestions */}
            <textarea
              id="comments"
              placeholder="Add your comments here..."
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              style={{
                width: '100%',
                height: '150px',
                padding: '15px',
                marginTop: '10px',
                marginBottom: '15px'
              }}
            />
            
            {/* Button to re-generate the cover letter using the provided comments */}
            <button 
              onClick={(e) => handleSubmit(e, true)}
              disabled={loading}
            >
              {loading && <div className="spinner"></div>}
              {loading ? 'Re-generating...' : 'Re-generate with Comments'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
