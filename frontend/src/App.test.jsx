import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import App from './App';

function fillRequiredFields() {
  const resume = new File(['%PDF-test'], 'resume.pdf', {
    type: 'application/pdf',
  });
  fireEvent.change(screen.getByLabelText(/resume pdf/i), {
    target: { files: [resume] },
  });
  fireEvent.change(screen.getByLabelText(/linkedin job posting url/i), {
    target: { value: 'https://www.linkedin.com/jobs/view/123456789' },
  });
}

beforeEach(() => {
  global.fetch = vi.fn();
  window.URL.createObjectURL = vi.fn(() => 'blob:test-pdf');
  window.URL.revokeObjectURL = vi.fn();
  Element.prototype.scrollIntoView = vi.fn();
});

afterEach(() => {
  vi.restoreAllMocks();
});

test('renders the project workflow and privacy note', () => {
  render(<App />);

  expect(screen.getByRole('heading', { name: /auto cover letter/i })).toBeInTheDocument();
  expect(screen.getByLabelText(/resume pdf/i)).toHaveAttribute('accept', 'application/pdf,.pdf');
  expect(screen.getByText(/resume and job text are sent/i)).toBeInTheDocument();
});

test('submits the documented multipart API fields and displays LaTeX', async () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ coverLetter: '\\documentclass{article}' }),
  });
  render(<App />);
  fillRequiredFields();
  fireEvent.change(screen.getByLabelText(/extra details/i), {
    target: { value: 'Built internal tools' },
  });
  fireEvent.change(screen.getByLabelText(/writing tone/i), {
    target: { value: 'traditional' },
  });

  fireEvent.click(screen.getByRole('button', { name: /generate cover letter/i }));

  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
  const [url, options] = fetch.mock.calls[0];
  expect(url).toBe('/api/generate-cover-letter');
  expect(options.method).toBe('POST');
  expect(options.body.get('jobUrl')).toContain('linkedin.com/jobs/view/123456789');
  expect(options.body.get('extraDetails')).toBe('Built internal tools');
  expect(options.body.get('tone')).toBe('traditional');
  expect(await screen.findByDisplayValue('\\documentclass{article}')).toBeInTheDocument();
});

test('shows the generating state while the request is pending', async () => {
  let resolveRequest;
  fetch.mockReturnValueOnce(new Promise((resolve) => {
    resolveRequest = resolve;
  }));
  render(<App />);
  fillRequiredFields();

  fireEvent.click(screen.getByRole('button', { name: /generate cover letter/i }));
  expect(screen.getByRole('button', { name: /generating/i })).toBeDisabled();

  resolveRequest({
    ok: true,
    json: async () => ({ coverLetter: '\\documentclass{article}' }),
  });
  expect(await screen.findByDisplayValue('\\documentclass{article}')).toBeInTheDocument();
});

test('surfaces API validation errors', async () => {
  fetch.mockResolvedValueOnce({
    ok: false,
    json: async () => ({ error: 'Enter a valid HTTPS LinkedIn job posting URL.' }),
  });
  render(<App />);
  fillRequiredFields();

  fireEvent.click(screen.getByRole('button', { name: /generate cover letter/i }));

  expect(await screen.findByRole('alert')).toHaveTextContent(/valid https linkedin/i);
});

test('rejects a non-PDF resume before calling the API', () => {
  render(<App />);
  const documentFile = new File(['resume'], 'resume.docx', {
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  });

  fireEvent.change(screen.getByLabelText(/resume pdf/i), {
    target: { files: [documentFile] },
  });

  expect(screen.getByRole('alert')).toHaveTextContent(/choose a pdf resume/i);
  expect(fetch).not.toHaveBeenCalled();
});

test('downloads the compiled PDF and releases the object URL', async () => {
  fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ coverLetter: '\\documentclass{article}' }),
    })
    .mockResolvedValueOnce({
      ok: true,
      blob: async () => new Blob(['pdf'], { type: 'application/pdf' }),
    });
  const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
  render(<App />);
  fillRequiredFields();
  fireEvent.click(screen.getByRole('button', { name: /generate cover letter/i }));
  await screen.findByDisplayValue('\\documentclass{article}');

  fireEvent.click(screen.getByRole('button', { name: /download pdf/i }));

  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
  expect(fetch.mock.calls[1][0]).toBe('/api/compile-latex');
  await waitFor(() => expect(clickSpy).toHaveBeenCalled());
  expect(window.URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-pdf');
});
