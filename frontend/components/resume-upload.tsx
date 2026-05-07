"use client";

import { useRef, useState } from "react";
import { FileUp, Loader2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function ResumeUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);

  async function upload(file: File) {
    setIsUploading(true);
    setStatus("");
    setFileName(file.name);

    const body = new FormData();
    body.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/profile/resume-upload`, {
        method: "POST",
        body
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const result = (await response.json()) as { message: string };
      setStatus(result.message);
    } catch {
      setStatus("Upload could not reach the backend. Start Docker Compose, then try again.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="rounded-md border border-line bg-paper p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-base font-semibold">Resume file</h2>
          <p className="mt-1 text-sm text-steel">
            Upload your master resume as PDF, DOC, or DOCX.
          </p>
          {fileName ? <p className="mt-2 text-sm font-medium">{fileName}</p> : null}
          {status ? <p className="mt-1 text-sm text-steel">{status}</p> : null}
        </div>
        <input
          ref={inputRef}
          className="hidden"
          type="file"
          accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              void upload(file);
            }
          }}
        />
        <button
          className="inline-flex items-center justify-center gap-2 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-70"
          disabled={isUploading}
          type="button"
          onClick={() => inputRef.current?.click()}
        >
          {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileUp className="h-4 w-4" />}
          {isUploading ? "Uploading" : "Upload resume"}
        </button>
      </div>
    </section>
  );
}
