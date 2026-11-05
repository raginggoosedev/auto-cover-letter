import React, { useState } from 'react';
import './App.css';

async function responseError(response, fallbackMessage) {
  try {
    const data = await response.json();
    return data.error || fallbackMessage;
  } catch (_error) {
    return fallbackMessage;
  }
}

function App() {
  const [tone, setTone] = useState('modern');
  const [resume, setResume] = useState(null);
  const [jobUrl, setJobUrl] = useState('');
  const [extraDetails, setExtraDetails] = useState('');
  const [coverLetter, setCoverLetter] = useState('');
  const [comments, setComments] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState('');

  const handleResumeChange = (event) => {
    const selectedFile = event.target.files?.[0] || null;
    if (selectedFile && !selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setResume(null);
      setError('Please choose a PDF resume.');
      event.target.value = '';
      return;
    }
    setResume(selectedFile);
    setError('');
  };

  const handleSubmit = async (event, regenerate = false) => {
    event.preventDefault();
    setError('');

    if (!resume) {
      setError('Please choose a PDF resume.');
      return;
    }
    if (!jobUrl.trim()) {
      setError('Please enter a LinkedIn job posting URL.');
      return;
    }

    const formData = new FormData();
    formData.append('resume', resume);
    formData.append('jobUrl', jobUrl.trim());
    formData.append('extraDetails', extraDetails.trim());
    formData.append('tone', tone);
    if (regenerate && comments.trim()) {
      formData.append('comments', comments.trim());
    }

    setIsGenerating(true);
    try {
      const response = await fetch('/api/generate-cover-letter', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error(await responseError(response, 'Cover letter generation failed.'));
      }
      const data = await response.json();
      setCoverLetter(data.coverLetter);
      setTimeout(() => {
        document.getElementById('generated-letter')?.scrollIntoView?.({
          behavior: 'smooth',
          block: 'start',
        });
      }, 0);
    } catch (requestError) {
      setError(requestError.message || 'Cover letter generation failed.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    setError('');
    setIsDownloading(true);
    try {
      const response = await fetch('/api/compile-latex', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latex: coverLetter }),
      });
      if (!response.ok) {
        throw new Error(await responseError(response, 'PDF compilation failed.'));
      }

      const blob = await response.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = 'cover-letter.pdf';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(objectUrl);
    } catch (requestError) {
      setError(requestError.message || 'PDF compilation failed.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="eyebrow">DataQuest 2025 hackathon project</p>
        <h1>Auto Cover Letter</h1>
        <p className="intro">
          Turn a PDF resume and LinkedIn job posting into an editable, tailored
          cover letter, then export it as a polished PDF.
        </p>

        <form className="generator-form" onSubmit={handleSubmit}>
          <label htmlFor="resume">Resume PDF</label>
          <input
            id="resume"
            type="file"
            accept="application/pdf,.pdf"
            onChange={handleResumeChange}
          />

          <label htmlFor="jobUrl">LinkedIn job posting URL</label>
          <input
            id="jobUrl"
            type="url"
            placeholder="https://www.linkedin.com/jobs/view/..."
            value={jobUrl}
            onChange={(event) => setJobUrl(event.target.value)}
          />

          <label htmlFor="extraDetails">Extra details <span>(optional)</span></label>
          <textarea
            id="extraDetails"
            rows="3"
            placeholder="Anything factual you want the letter to emphasize"
            value={extraDetails}
            onChange={(event) => setExtraDetails(event.target.value)}
          />

          <label htmlFor="tone">Writing tone</label>
          <select
            id="tone"
            value={tone}
            onChange={(event) => setTone(event.target.value)}
          >
            <option value="modern">Modern and direct</option>
            <option value="traditional">Traditional and formal</option>
            <option value="creative">Creative and engaging</option>
          </select>

          <p className="privacy-note">
            Privacy note: resume and job text are sent to the configured OpenAI
            API project. This showcase does not intentionally retain uploads.
          </p>

          <button className="primary-button" type="submit" disabled={isGenerating}>
            {isGenerating && <span className="spinner" aria-hidden="true" />}
            {isGenerating ? 'Generating…' : 'Generate cover letter'}
          </button>
        </form>

        {error && <p className="error-message" role="alert">{error}</p>}
      </section>

      {coverLetter && (
        <section id="generated-letter" className="result-panel">
          <div className="result-heading">
            <div>
              <p className="eyebrow">Generated output</p>
              <h2>Review the LaTeX before export</h2>
            </div>
            <button
              className="secondary-button"
              type="button"
              onClick={handleDownload}
              disabled={isDownloading}
            >
              {isDownloading && <span className="spinner" aria-hidden="true" />}
              {isDownloading ? 'Creating PDF…' : 'Download PDF'}
            </button>
          </div>

          <label className="sr-only" htmlFor="coverLetter">Generated cover letter LaTeX</label>
          <textarea
            id="coverLetter"
            className="latex-editor"
            value={coverLetter}
            onChange={(event) => setCoverLetter(event.target.value)}
          />

          <div className="revision-box">
            <label htmlFor="comments">Revision instructions <span>(optional)</span></label>
            <textarea
              id="comments"
              rows="4"
              placeholder="For example: make the opening more concise"
              value={comments}
              onChange={(event) => setComments(event.target.value)}
            />
            <button
              className="primary-button"
              type="button"
              onClick={(event) => handleSubmit(event, true)}
              disabled={isGenerating}
            >
              {isGenerating && <span className="spinner" aria-hidden="true" />}
              {isGenerating ? 'Regenerating…' : 'Regenerate with feedback'}
            </button>
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
