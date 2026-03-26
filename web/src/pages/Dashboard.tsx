import { useQuery } from '@tanstack/react-query'
import { reportAPI, complianceAPI, partyAPI } from '../lib/api'
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  AlertTriangle,
  Calendar,
  FileText
} from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { data: reports } = useQuery({
    queryKey: ['dashboard-reports'],
    queryFn: () => reportAPI.trialBalance(),
  })

  const { data: compliance } = useQuery({
    queryKey: ['compliance-calendar'],
    queryFn: () => complianceAPI.calendar(),
  })

  const { data: parties } = useQuery({
    queryKey: ['parties'],
    queryFn: () => partyAPI.list(),
  })

  const stats = [
    {
      name: 'Total Assets',
      value: `₹${reports?.data?.assets?.toLocaleString() || '0'}`,
      change: '+12%',
      trend: 'up',
      icon: TrendingUp,
    },
    {
      name: 'Total Liabilities',
      value: `₹${reports?.data?.liabilities?.toLocaleString() || '0'}`,
      change: '-5%',
      trend: 'down',
      icon: TrendingDown,
    },
    {
      name: 'Outstanding Receivables',
      value: `₹${reports?.data?.outstanding?.toLocaleString() || '0'}`,
      change: '+8%',
      trend: 'up',
      icon: Users,
    },
    {
      name: 'Compliance Alerts',
      value: compliance?.data?.overdue?.length || 0,
      change: '',
      trend: 'neutral',
      icon: AlertTriangle,
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of your financial health</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</p>
                {stat.change && (
                  <p className={`text-sm mt-2 ${
                    stat.trend === 'up' ? 'text-green-600' : 
                    stat.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {stat.change} from last month
                  </p>
                )}
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <stat.icon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Compliance Calendar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Compliance Calendar</h2>
            <Link to="/compliance" className="text-sm text-blue-600 hover:text-blue-700">
              View All
            </Link>
          </div>
          
          <div className="space-y-4">
            {compliance?.data?.upcoming?.slice(0, 5).map((item: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    item.status === 'overdue' ? 'bg-red-500' :
                    item.status === 'due-soon' ? 'bg-yellow-500' : 'bg-green-500'
                  }`} />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.return_type}</p>
                    <p className="text-xs text-gray-500">Due: {item.due_date}</p>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  item.status === 'overdue' ? 'bg-red-100 text-red-700' :
                  item.status === 'due-soon' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
                }`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Vouchers</h2>
            <Link to="/vouchers" className="text-sm text-blue-600 hover:text-blue-700">
              View All
            </Link>
          </div>
          
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Receipt #{1000 + i}</p>
                    <p className="text-xs text-gray-500">Sharma Traders</p>
                  </div>
                </div>
                <span className="text-sm font-medium text-gray-900">₹{(i * 5000).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
