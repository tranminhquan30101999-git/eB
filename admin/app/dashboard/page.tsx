"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, CheckCircle, Clock, Star, TrendingUp, Users, FilePlus2, Loader2 } from "lucide-react";

const API_BASE_URL = "http://localhost:8080/api/v1";

interface DashboardData {
  totalBookings: number;
  completionRate: number;
  todaysBookings: number;
  cancellationRate: number;
}
interface RecentBooking {
  id: number;
  customer_name: string;
  service: {
    name: string;
  };
  time_slot: {
    start_time: string;
  };
  status: string;
}

const statusColors = {
  scheduled: "bg-blue-50 border border-blue-200 text-blue-700",
  "checked-in": "bg-yellow-50 border border-yellow-200 text-yellow-700",
  serving: "bg-green-50 border border-green-200 text-green-700",
  completed: "bg-gray-50 border border-gray-200 text-gray-700",
  cancelled: "bg-red-50 border border-red-200 text-red-700",
};

export default function DashboardPage() {
  const [kpiData, setKpiData] = useState<DashboardData>({
    totalBookings: 0,
    completionRate: 0,
    todaysBookings: 0,
    cancellationRate: 0,
  });
  const [recentBookings, setRecentBookings] = useState<RecentBooking[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/admin/dashboard/summary`);
      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
      }
      const data = await response.json();
      setKpiData(data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setKpiData({
        totalBookings: 0,
        completionRate: 0,
        todaysBookings: 0,
        cancellationRate: 0,
      });
    } finally {
      setIsLoading(false);
    }
  };
  const fetchRecentBookingData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/admin/dashboard/recent-bookings`);
      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
      }
      const data = await response.json();
      setRecentBookings(data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setRecentBookings([]);
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    fetchDashboardData();
    fetchRecentBookingData();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your booking and knowledge management system
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="shadow-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Today Bookings</CardTitle>
            <Clock className="h-5 w-5 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {isLoading ? <Loader2 className="animate-spin" /> : `${kpiData.todaysBookings}`}
            </div>
          </CardContent>
        </Card>
        <Card className="shadow-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Total Bookings</CardTitle>
            <Calendar className="h-5 w-5 text-indigo-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {isLoading ? <Loader2 className="animate-spin" /> : kpiData.totalBookings}
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Completion Rate</CardTitle>
            <CheckCircle className="h-5 w-5 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {isLoading ? <Loader2 className="animate-spin" /> : `${kpiData.completionRate.toFixed(1)}%`}
            </div>
          </CardContent>
        </Card>

        

        <Card className="shadow-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Cancellation Rate</CardTitle>
            <Star className="h-5 w-5 text-pink-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {isLoading ? <Loader2 className="animate-spin" /> : `${kpiData.cancellationRate.toFixed(1)}%`}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Bookings */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base font-semibold text-slate-700">
              <Calendar className="h-5 w-5 text-indigo-500" /> Recent Bookings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
              </div>
            ) : recentBookings.length === 0 ? (
              <div className="text-center py-4 text-slate-400">No recent bookings</div>
            ) : (
              recentBookings.map((booking) => (
                <div key={booking.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-slate-100 transition">
                  <div>
                    <p className="font-medium text-slate-700">{booking.customer_name}</p>
                    <p className="text-sm text-slate-500">
                      {booking.service.name} • {booking.time_slot.start_time}
                    </p>
                  </div>
                  <Badge className={statusColors[booking.status as keyof typeof statusColors]}>
                    {booking.status}
                  </Badge>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card className="shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base font-semibold text-slate-700">
              <TrendingUp className="h-5 w-5 text-green-500" /> Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <a href="/dashboard/booking" className="block">
              <div className="flex items-center gap-3 p-4 border rounded-lg hover:bg-slate-100 transition">
                <Users className="h-6 w-6 text-blue-600" />
                <div>
                  <p className="font-medium text-slate-700">View Booking Board</p>
                  <p className="text-sm text-slate-500">Manage customer bookings</p>
                </div>
              </div>
            </a>

            <a href="/dashboard/knowledge" className="block">
              <div className="flex items-center gap-3 p-4 border rounded-lg hover:bg-slate-100 transition">
                <FilePlus2 className="h-6 w-6 text-green-600" />
                <div>
                  <p className="font-medium text-slate-700">Upload Documents</p>
                  <p className="text-sm text-slate-500">Add to knowledge base</p>
                </div>
              </div>
            </a>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
