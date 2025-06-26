"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { 
  Upload,
  FileText,
  MoreVertical,
  Search,
  Download,
  Trash2,
  Eye,
  Tag,
  Calendar,
  HardDrive,
  AlertCircle,
  CheckCircle,
  Clock
} from "lucide-react";
import { format } from "date-fns";

type DocumentStatus = "processing" | "ready" | "error";

interface Document {
  id: number;
  title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  tags: string;
  status: DocumentStatus;
  error_message?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const API_BASE_URL = "http://localhost:8080/api/v1";

const statusColors = {
  processing: "bg-yellow-100 text-yellow-800",
  ready: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
};

const statusLabels = {
  processing: "Processing",
  ready: "Ready",
  error: "Error",
};

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

function FileUploadArea({ onUploadComplete }: { onUploadComplete: () => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Only set isDragging to false if we're leaving the drop zone entirely
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;
    
    if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      console.log("Dropped files:", files); // Debug log
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      console.log("Selected files:", files); // Debug log
      handleFileUpload(files[0]);
    }
    // Reset the input value so the same file can be selected again
    e.target.value = '';
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (file: File) => {
    console.log("Starting file upload:", file.name, file.type, file.size); // Debug log
    setIsUploading(true);
    setUploadStatus("");

    // Validate file type
    const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      setUploadStatus(`File type ${fileExtension} not supported. Please use: ${allowedTypes.join(', ')}`);
      setIsUploading(false);
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setUploadStatus(`File too large. Maximum size is 10MB, your file is ${formatFileSize(file.size)}`);
      setIsUploading(false);
      return;
    }

    try {
      console.log("Creating FormData and sending request to:", `${API_BASE_URL}/knowledge/documents/upload`);
      
      const formData = new FormData();
      formData.append("file", file);
      formData.append("title", file.name);
      
      const response = await fetch(`${API_BASE_URL}/knowledge/documents/upload`, {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", response.status, response.statusText);

      if (!response.ok) {
        let errorMessage = "Upload failed";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || `Server error: ${response.status}`;
        } catch {
          errorMessage = `Server error: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log("Upload successful:", result);
      setUploadStatus(`✓ Successfully uploaded: ${result.filename}`);
      onUploadComplete();
      
      // Clear status after 3 seconds
      setTimeout(() => setUploadStatus(""), 3000);
      
    } catch (error) {
      console.error("Upload error:", error);
      const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
      setUploadStatus(`✗ Upload failed: ${errorMessage}`);
      
      // Clear error after 8 seconds
      setTimeout(() => setUploadStatus(""), 8000);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload Documents
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 hover:border-gray-400"
          }`}
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium mb-2">
            Drag and drop files here, or click to select
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Supports: PDF, DOC, DOCX, TXT (max 10MB)
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleFileSelect}
            className="hidden"
            disabled={isUploading}
          />
          <Button 
            variant="outline" 
            onClick={handleButtonClick}
            disabled={isUploading}
            className="cursor-pointer"
          >
            {isUploading ? "Uploading..." : "Choose Files"}
          </Button>
          
          {uploadStatus && (
            <div className={`mt-4 p-2 rounded ${
              uploadStatus.includes("failed") || uploadStatus.includes("error") 
                ? "bg-red-50 text-red-700" 
                : "bg-green-50 text-green-700"
            }`}>
              {uploadStatus}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [backendStatus, setBackendStatus] = useState<"checking" | "connected" | "disconnected">("checking");

  const testBackendConnection = async () => {
    try {
      setBackendStatus("checking");
      const response = await fetch(`${API_BASE_URL}/health`, { 
        method: 'GET',
        cache: 'no-cache'
      });
      
      if (response.ok) {
        setBackendStatus("connected");
        return true;
      } else {
        setBackendStatus("disconnected");
        return false;
      }
    } catch (err) {
      console.error("Backend connection test failed:", err);
      setBackendStatus("disconnected");
      return false;
    }
  };

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      
      // Test backend connection first
      const isConnected = await testBackendConnection();
      if (!isConnected) {
        throw new Error("Backend server is not accessible");
      }

      const response = await fetch(
        `${API_BASE_URL}/knowledge/documents?search=${encodeURIComponent(searchTerm)}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch documents`);
      }
      
      const data = await response.json();
      setDocuments(data);
      setError("");
    } catch (err) {
      console.error("Error fetching documents:", err);
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(`Failed to load documents: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (searchTerm !== "") {
        fetchDocuments();
      }
    }, 500);

    return () => clearTimeout(debounceTimer);
  }, [searchTerm]);

  const handleDelete = async (documentId: number) => {
    if (!confirm("Are you sure you want to delete this document?")) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/knowledge/documents/${documentId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete document");
      }

      // Refresh the documents list
      await fetchDocuments();
    } catch (err) {
      console.error("Error deleting document:", err);
      alert("Failed to delete document");
    }
  };

  const getStatusIcon = (status: DocumentStatus) => {
    switch (status) {
      case "ready":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "processing":
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-600" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
          <p className="text-muted-foreground">
            Manage documents and resources for your chatbot
          </p>
          <div className="flex items-center gap-2 mt-2">
            <div className={`inline-flex items-center gap-1 text-sm ${
              backendStatus === "connected" ? "text-green-600" : 
              backendStatus === "disconnected" ? "text-red-600" : "text-yellow-600"
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                backendStatus === "connected" ? "bg-green-500" : 
                backendStatus === "disconnected" ? "bg-red-500" : "bg-yellow-500"
              }`} />
              Backend: {backendStatus === "connected" ? "Connected" : 
                       backendStatus === "disconnected" ? "Disconnected" : "Checking..."}
            </div>
            {backendStatus === "disconnected" && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={testBackendConnection}
                className="text-xs py-1 px-2 h-6"
              >
                Test Connection
              </Button>
            )}
          </div>
        </div>
      </div>

      <FileUploadArea onUploadComplete={fetchDocuments} />

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <div className="font-medium">Connection Error</div>
          <div className="text-sm mt-1">{error}</div>
          <div className="text-xs mt-2 text-red-600">
            Make sure the backend server is running on <code>localhost:8080</code>
          </div>
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Documents ({documents.length})
            </CardTitle>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search documents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <Button 
                variant="outline" 
                onClick={fetchDocuments}
                disabled={isLoading}
              >
                {isLoading ? "Loading..." : "Refresh"}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No documents found</p>
              <p className="text-sm text-gray-500">Upload some documents to get started</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Tags</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Updated</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((document) => (
                  <TableRow key={document.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="flex-shrink-0">
                          <FileText className="h-4 w-4 text-gray-500" />
                        </div>
                        <div>
                          <p className="font-medium">{document.title}</p>
                          <p className="text-sm text-gray-500">{document.file_type.toUpperCase()}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {document.tags ? document.tags.split(',').map((tag, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            <Tag className="h-2 w-2 mr-1" />
                            {tag.trim()}
                          </Badge>
                        )) : (
                          <span className="text-gray-400 text-sm">No tags</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <HardDrive className="h-3 w-3 text-gray-400" />
                        {formatFileSize(document.file_size)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(document.status)}
                        <Badge 
                          className={statusColors[document.status]}
                          variant="secondary"
                        >
                          {statusLabels[document.status]}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Calendar className="h-3 w-3" />
                        {format(new Date(document.updated_at), "MMM dd, yyyy")}
                      </div>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <MoreVertical className="h-3 w-3" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Eye className="mr-2 h-3 w-3" />
                            View
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Download className="mr-2 h-3 w-3" />
                            Download
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-red-600"
                            onClick={() => handleDelete(document.id)}
                          >
                            <Trash2 className="mr-2 h-3 w-3" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}