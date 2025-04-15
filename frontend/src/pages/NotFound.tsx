import { Link } from "react-router-dom";

function NotFound() {
  const page = "/";
  return (
    <div
      className="disableMargin h-screen flex flex-col justify-center items-center"
    >
      <div className="text-4xl font-bold text-gray-800  dark:text-gray-300 mb-8">404 Not Found</div>
      <Link
        to={page}
        className="px-6 py-3 bg-blue-500 text-white rounded-md text-lg font-semibold hover:bg-blue-600 transition-colors"
      >
        Go to Home
      </Link>
    </div>
  );
}

export default NotFound;