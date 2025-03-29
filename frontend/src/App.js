import logo from './logo.svg';
import './App.css';
import React, { useState } from 'react';
import axios from 'axios';


function App() {
  // State variables to manage the resume, job URL, extra details, cover letter, and loading state
  const [resume , setResume] = useState(null);
  const [jobURL , setJobURL] = useState('');
  const [extraDetails , setExtraDetails] = useState('');
  const [coverLetter , setCoverLetter] = useState('');
  const [loading , setLoading] = useState(false);

  // Handle file upload and set the resume state
  const handleResumeChange = (event) => {
    setResume(event.target.files[0]);
  }

  // Handle form submission to generate the cover letter
  const handleSubmit = async (event) => {
    event.preventDefault();

    // Validate that resume and job URL are provided
    if (!resume || !jobURL) {
      alert('Please upload a resume and enter a job name.');
      return;
    }
    
    setLoading(true);
    // Create a FormData object to send the resume and other details
    const formData = new FormData();
    formData.append('resume', resume);
    formData.append('jobName', jobURL);
    formData.append('extraDetails', extraDetails);

    // Send a POST request to the backend server to generate the cover letter
    try {
      console.log(formData);
      console.log(formData.get('resume'));
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
  }

  // Handle download of the generated cover letter
  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([coverLetter], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Render the main application component
  return (
    <div className="App">
      <header className="App-header">
        <h1>Cover letter generator</h1>
      </header>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf,.doc,.docx" onChange={handleResumeChange} required />
        <input type="text" placeholder="Enter Job URL" value={jobURL} onChange={(e) => setJobURL(e.target.value)} required />
        <input type="text" placeholder="Enter any extra details you wish to add" value={extraDetails} onChange={(e) => setExtraDetails(e.target.value)} required />
        <button type="submit" disabled={loading}>{loading ? 'Generating...' : 'Generate Cover Letter'}</button>
      </form>

      {coverLetter && (
        <div className="cover-letter-container">
          <h2>Generated Cover Letter</h2>
          <textarea value={coverLetter} readOnly rows={10} cols={50} />
          <button onClick={handleDownload}>Download Cover Letter</button>
        </div>
      )}
    </div>
  );
}

export default App;
