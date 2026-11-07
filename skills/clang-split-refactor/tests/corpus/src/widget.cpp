#include "widget.hpp"
#include "config.hpp"

#include <map>
#include <memory>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

#if defined(_WIN32)
	#include <windows.h>
#endif

namespace demo {
	namespace {
		// Overloads move together.
		std::string describe(int value) {
			return "int:" + std::to_string(value);
		}

		std::string describe(const std::string& value) {
			return "str:" + value;
		}

		// Used only from a generic lambda, so libclang does not resolve the call.
		int twice(int value) {
			return value * 2;
		}
	}

	// A deduced return type stays in the header.
	auto sum_of(const std::vector<int>& values) {
		return std::accumulate(values.begin(), values.end(), 0);
	}

	constexpr int square(int value) {
		return value * value;
	}

	class Shape {
	public:
		virtual ~Shape() = default;

		virtual std::string name() const {
			return "shape";
		}

		[[nodiscard]] virtual int area() const {
			return 0;
		}
	};

	class Widget final : public Shape {
	public:
		struct Options {
			int scale = 1;

			int scaled(int value) const {
				return value * scale;
			}
		};

		explicit Widget(std::string label, int scale = 1)
			: label_(std::move(label)), options_{scale}, weights_{1, 2, 3} {
		}

		std::string name() const override {
			return "widget:" + label_;
		}

		[[nodiscard]] int area() const override {
			return options_.scaled(sum_of(weights_));
		}

		static int fold(std::vector<std::vector<int>> rows = std::vector<std::vector<int>>{{1, 2}, {3}}, int bias = square(2)) {
			int total = bias;
			for (const auto& row : rows) {
				total += sum_of(row);
			}
			return total;
		}

		std::string report() const {
			std::ostringstream out;
			auto apply = [](auto value) { return twice(value); };
			out << name() << ' ' << area() << ' ' << apply(area()) << ' ' << describe(label_) << ' ' << describe(fold());
#if DEMO_FEATURE
			out << " feature";
#else
			out << " plain";
#endif
#if DEMO_VERBOSE
			out << " verbose";
#endif
			return out.str();
		}

	private:
		std::string label_;
		Options options_;
		std::vector<int> weights_;
	};

	std::string run_demo() {
		std::map<std::string, std::unique_ptr<Shape>> shapes;
		shapes["a"] = std::make_unique<Widget>("alpha", 3);
		shapes["b"] = std::make_unique<Shape>();
		std::ostringstream out;
		for (const auto& [key, shape] : shapes) {
			out << key << '=' << shape->name() << ' ' << shape->area() << '\n';
		}
		out << Widget("beta").report() << '\n';
		return out.str();
	}
}
