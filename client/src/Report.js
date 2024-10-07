import React, { useState, useEffect } from 'react';

const CourseReport = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/report'); //Change this api endpoint.
        if (!response.ok) {
          throw new Error('Failed to fetch report data');
        }
        const data = await response.json();
        setReportData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchReportData();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!reportData) {
    return <div>No data available.</div>;
  }

  return (
    <div className="bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Course Report</h1>

        {/* Elective Credits Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Elective Credits</h2>
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Elective Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Credits
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(reportData.elective_credits).map(([elective, credits], index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">{elective}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{credits}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Missing Courses Section */}
        {reportData.missing_courses && Object.keys(reportData.missing_courses).length > 0 && (
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Missing Courses</h2>
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Course Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Course Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Elective Type
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Object.entries(reportData.missing_courses).map(([courseCode, courseInfo], index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap">{courseCode}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{courseInfo.title}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{courseInfo.elective_type}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* All Courses Section */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">All Courses</h2>
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Course Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Course Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Credits
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reg. Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Elective Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Grade
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reportData.courses.map((course, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">{course[0]}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{course[1]}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{course[2]}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{course[3]}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{course[4]}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{course[5]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};

export default CourseReport;
