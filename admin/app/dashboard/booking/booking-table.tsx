import { useState, useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Phone,
  Calendar,
  Clock,
  MoreVertical,
  ChevronUp,
  ChevronDown,
} from "lucide-react";
import { Booking, BookingStatus } from "./type/booking-status";
import { Pagination } from "@/components/ui/pagination";
import { useMediaQuery } from "usehooks-ts"; // cần cài thêm: npm install usehooks-ts

type Props = {
  bookings: Booking[];
  onStatusChange: (bookingId: number, newStatus: BookingStatus) => void;
};

function BookingTable({ bookings, onStatusChange }: Props) {
  const isMobile = useMediaQuery("(max-width: 768px)");

  const [sortKey, setSortKey] = useState<keyof Booking>("customer_name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const allStatuses: BookingStatus[] = ["scheduled", "checked-in", "serving", "completed", "cancelled"];

  const handleSort = (key: keyof Booking) => {
    if (sortKey === key) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortOrder("asc");
    }
  };

  const sortedData = useMemo(() => {
    return [...bookings].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];

      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortOrder === "asc"
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      return 0;
    });
  }, [bookings, sortKey, sortOrder]);

  const pagedData = sortedData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const getServiceColor = (serviceName: string): string => {
    const colors = {
      "Làm móng gel": "bg-purple-100 text-purple-800",
      "Làm móng gel kèm vẽ": "bg-pink-100 text-pink-800",
      "Sơn móng thường": "bg-blue-100 text-blue-800",
      "Cắt và dũa móng": "bg-green-100 text-green-800",
      "Làm móng đính đá": "bg-yellow-100 text-yellow-800",
      "Tẩy và làm lại móng": "bg-indigo-100 text-indigo-800",
    };
    return colors[serviceName as keyof typeof colors] || "bg-gray-100 text-gray-800";
  };

  const statusColorMap: Record<BookingStatus, string> = {
    scheduled: "bg-blue-100 text-blue-800",
    "checked-in": "bg-purple-100 text-purple-800",
    serving: "bg-yellow-100 text-yellow-800",
    completed: "bg-green-100 text-green-800",
    cancelled: "bg-red-100 text-red-800",
  };

  const renderSortIcon = (key: keyof Booking) => {
    if (sortKey !== key) return null;
    return sortOrder === "asc" ? (
      <ChevronUp className="inline h-3 w-3 ml-1" />
    ) : (
      <ChevronDown className="inline h-3 w-3 ml-1" />
    );
  };

  if (isMobile) {
    return (
      <div className="space-y-3">
        {pagedData.map((booking) => {
          const initials = booking.customer_name
            .split(" ")
            .map((name) => name[0])
            .join("")
            .toUpperCase();

          const availableStatuses = allStatuses.filter(status => status !== booking.status);

          return (
            <div key={booking.id} className="rounded-lg border p-3 shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <Avatar className="h-10 w-10">
                  <AvatarFallback>{initials}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium text-base">{booking.customer_name}</p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Phone className="h-3 w-3" /> {booking.customer_phone}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 text-xs mb-2">
                <Badge className={getServiceColor(booking.service.name)}>{booking.service.name}</Badge>
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {new Date(booking.time_slot.date).toLocaleDateString()} {booking.time_slot.start_time}
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {booking.service.duration_minutes} phút
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className={`inline-flex items-center px-2 py-1 rounded-full font-medium text-xs ${statusColorMap[booking.status]}`}>
                  {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                </span>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                      <MoreVertical className="h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    {availableStatuses.map(status => (
                      <DropdownMenuItem
                        key={status}
                        onClick={() => onStatusChange(booking.id, status)}
                      >
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          );
        })}

        <div className="flex justify-center">
          <Pagination
            total={Math.ceil(sortedData.length / pageSize)}
            page={currentPage}
            onPageChange={setCurrentPage}
          />
        </div>
      </div>
    );
  }

  // Desktop Table view
  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[200px] cursor-pointer" onClick={() => handleSort("customer_name")}>
              Khách hàng {renderSortIcon("customer_name")}
            </TableHead>
            <TableHead className="w-[150px]">Dịch vụ</TableHead>
            <TableHead className="w-[200px]">Thời gian</TableHead>
            <TableHead className="w-[100px]">Thời lượng</TableHead>
            <TableHead className="w-[100px]">Trạng thái</TableHead>
            <TableHead className="w-[200px]">Ghi chú</TableHead>
            <TableHead className="w-[50px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {pagedData.map((booking) => {
            const initials = booking.customer_name
              .split(" ")
              .map((name) => name[0])
              .join("")
              .toUpperCase();
            const availableStatuses = allStatuses.filter(status => status !== booking.status);

            return (
              <TableRow key={booking.id}>
                <TableCell>
                  <div className="flex items-center gap-3">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="text-xs">{initials}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium text-sm">{booking.customer_name}</p>
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <Phone className="h-3 w-3" /> {booking.customer_phone}
                      </p>
                    </div>
                  </div>
                </TableCell>

                <TableCell>
                  <Badge className={getServiceColor(booking.service.name)} variant="secondary">
                    {booking.service.name}
                  </Badge>
                </TableCell>

                <TableCell>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Calendar className="h-3 w-3" />
                    {new Date(booking.time_slot.date).toLocaleDateString()} {booking.time_slot.start_time}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {booking.service.duration_minutes} phút
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1 text-xs">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full font-medium ${statusColorMap[booking.status]}`}>
                      {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <p className="text-xs text-gray-600">{booking.notes || "-"}</p>
                </TableCell>

                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                        <MoreVertical className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {availableStatuses.map(status => (
                        <DropdownMenuItem
                          key={status}
                          onClick={() => onStatusChange(booking.id, status)}
                        >
                          {status.charAt(0).toUpperCase() + status.slice(1)}
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <div className="flex justify-end">
        <Pagination
          total={Math.ceil(sortedData.length / pageSize)}
          page={currentPage}
          onPageChange={setCurrentPage}
        />
      </div>
    </div>
  );
}

export default BookingTable;
