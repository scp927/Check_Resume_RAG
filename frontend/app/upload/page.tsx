"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardTitle } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

type UploadStatus = {
  batch_id: string;
  status: string;
  total: number;
  processed: number;
  message: string;
};

export default function UploadPage() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [status, setStatus] = useState<UploadStatus | null>(null);
  const [loading, setLoading] = useState(false);

  async function upload() {
    if (!files?.length) return;
    setLoading(true);
    const form = new FormData();
    Array.from(files).forEach((file) => form.append("files", file));
    const response = await fetch(`${API_BASE}/upload/resumes`, { method: "POST", body: form });
    const nextStatus = (await response.json()) as UploadStatus;
    setStatus(nextStatus);
    setLoading(false);
  }

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-3xl font-bold">Batch Resume Upload</h1>
      </section>
      <Card>
        <CardTitle>Upload resumes</CardTitle>
        <div className="mt-4 flex flex-col gap-3">
          <input multiple type="file" accept=".pdf,.docx,.txt" onChange={(event) => setFiles(event.target.files)} />
          <Button className="w-fit" onClick={upload} disabled={loading || !files?.length}>{loading ? "Uploading..." : "Upload batch"}</Button>
        </div>
      </Card>
      {status && (
        <Card>
          <CardTitle>Processing status</CardTitle>
          <div className="mt-3 text-sm text-slate-600">{status.message}</div>
          <div className="mt-4 h-3 overflow-hidden border border-slate-200 bg-slate-100">
            <div className="h-full bg-blue-700" style={{ width: `${status.total ? (status.processed / status.total) * 100 : 0}%` }} />
          </div>
          <div className="mt-2 text-sm">{status.processed}/{status.total} · {status.status}</div>
        </Card>
      )}
    </div>
  );
}
