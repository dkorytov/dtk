#ifndef DTK_MATH_HPP
#define DTK_MATH_HPP
#include <cmath>
#include <cstdlib>
#include <random>
namespace dtk{
  std::default_random_engine dtk_random_engine;
  
  template<class T,class U>
  T max(T* data, U size){
    T max_val = data[0];
    for(U i =1;i<size;++i){
      if(data[i]>max_val)
	max_val = data[i];
    }
    return max_val;
  }
  template<class T,class U>
  T min(T* data, U size){
    T min_val = data[0];
    for(U i =1;i<size;++i){
      if(data[i]<min_val)
	min_val = data[i];
    }
    return min_val;
  }
  template<class T>
  T min(std::vector<T> data){
    return min(&data[0],data.size());
  }
  template<class T>
  T max(std::vector<T> data){
    return max(&data[0],data.size());
  }

  template<class T,class U>
  T average(T* data, U size){
    T result = 0;
    for(U i =0;i<size;++i){
      result += data[i];
    }
    return result/static_cast<T>(size);
  }
  template<class T>
  T average(std::vector<T> data){
    size_t size = data.size();
    T result = 0;
    for(size_t i =0;i<size;++i){
      result += data[i];
    }
    return result/static_cast<T>(size);

  }
  template<class T> 
  std::vector<T> linspace(T start,T end, int num){
    std::vector<T> result(num);
    T del=0;
    if(num != 0)
     del = (end-start)/num;
    for(int i =0;i<num-1;++i){
      result[i]=start+del*i;
    }
    result[num-1]=end; //to avoid round off errors.
    return result;
  }
  template<class T>
  std::vector<T> logspace(T start,T end, int num){
    std::vector<T> result = linspace(start,end,num);
    for(int i =0;i<result.size();++i){
      result[i] = std::pow(10,result[i]);
    }
    return result;
  }
  
  template<class T>
  T root_mean_squared(std::vector<T> data){
    T result =0;
    for(size_t i =0;i<data.size();++i){
      result+=data[i]*data[i];
    }
    return sqrt(result);
  }
  
  template<class T>
  T rand(){
    return (T) std::rand()/((T)RAND_MAX);
  }
  template<class T, class U>
  void rand_fill(T* array, U size){
    for(U i =0; i<size;++i)
      array[i] = rand<T>();
  }

  template<class T>
  T normal_random(T mean=0, T sigma=1){
    std::normal_distribution<T> norm(mean, sigma);
    return norm(dtk_random_engine);
  }
  template<class T>
  void normal_random(T mean, T sigma, T* output, size_t num){
    std::normal_distribution<T> norm(mean, sigma);
    for(size_t i=0;i<num;++i){
      output[i]=norm(dtk_random_engine);
      // std::cout<<<<std::endl;
    }
  }

  template<class T>
  void random_vector3d(T& x, T& y, T& z, T radius){
    std::normal_distribution<T> norm(0, 1);
    x = norm(dtk_random_engine);
    y = norm(dtk_random_engine);
    z = norm(dtk_random_engine);
    T r = std::sqrt(x*x + y*y + z*z);
    x = x/r * radius;
    y = y/r * radius;
    z = z/r * radius;
  }
}






#endif
