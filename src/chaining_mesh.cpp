#include "dtk/chaining_mesh.hpp"
#include "dtk/sort.hpp"
#include <set>
#include <cmath>
template<typename T>
void smart_delete(T* array){
  if(array)
    delete [] array;
}

namespace dtk{
  ChainingMeshIndex::ChainingMeshIndex(float* len_xyz, size_t* len_ijk, int dim_num):
    dim_num(dim_num),element_index(0), element_cell(0){
    length_xyz = new float[dim_num];
    length_ijk = new size_t[dim_num];
    cell_length_xyz = new float[dim_num];
    cell_ijk_offset = new size_t[dim_num];
    cell_num = 1;
    for(int i =0;i<dim_num;++i){
      length_xyz[i] = len_xyz[i];
      length_ijk[i] = len_ijk[i];
      cell_length_xyz[i] = length_xyz[i]/length_ijk[i];
      cell_num*=length_ijk[i];
    }
    size_t offset =1;
    for(int i=dim_num-1;i>-1;--i){
      cell_ijk_offset[i]=offset;
      offset*=length_ijk[i];
    }
    cell_start = new size_t[cell_num];
    cell_size  = new size_t[cell_num];
  }
  ChainingMeshIndex::ChainingMeshIndex():
    dim_num(0), element_index(0), element_cell(0),
    length_xyz(0), length_ijk(0), cell_length_xyz(0),
    cell_ijk_offset(0), cell_start(0), cell_size(0){}
  ChainingMeshIndex::~ChainingMeshIndex(){}
  void ChainingMeshIndex::clear(){
    smart_delete(length_xyz);
    smart_delete(length_ijk);
    smart_delete(element_index);
    smart_delete(element_cell);
    smart_delete(cell_start);
    smart_delete(cell_size);
    smart_delete(cell_ijk_offset);
  }
  void ChainingMeshIndex::set_grid(float* len_xyz, size_t* len_ijk, int dim_num){}
  void ChainingMeshIndex::place_onto_mesh(float** xyzs, size_t size){
    element_positions = new float*[dim_num];
    for(int i =0;i<dim_num;++i)
      element_positions[i] = xyzs[i];
    element_num = size;
    element_index = new size_t[size];
    element_cell  = new size_t[size];
    std::cout<<"assigning element cell ids"<<std::endl;
    assign_element_cell(element_positions, size);
    std::cout<<"figuring out groups of cell ids"<<std::endl;
    group_cells();
    
  }
  void ChainingMeshIndex::assign_element_cell(float** xyz, size_t size){
    float element_xyz[dim_num];
    for(size_t i=0; i<size;++i){
      for(int j =0;j<dim_num;++j){
	element_xyz[j]=xyz[j][i];
      }
      element_index[i] =i;
      element_cell[i] = get_cell_id_from_position(element_xyz);
      if(i%100000000==0)
	std::cout<<i<<":"<<element_cell[i]<<std::endl;
    }
  }
  void ChainingMeshIndex::group_cells(){
    std::cout<<"starting arg sort"<<std::endl;
    size_t* srt = arg_sort(element_cell, element_num);
    std::cout<<"reorder 1"<<std::endl;
    reorder(element_index, element_num, srt);
    std::cout<<"reorder 2"<<std::endl;
    reorder(element_cell,  element_num, srt);
    size_t element_i = 0;
    size_t cell_i =0;
    std::cout<<"cell starting assignments"<<std::endl;
    while(element_i < element_num && cell_i < cell_num){
      if(cell_i <= element_cell[element_i]){
	cell_start[cell_i] = element_i;
	++cell_i;
      }
      else
	++element_i;
    }
    std::cout<<"Wrapping up"<<std::endl;
    while(cell_i < cell_num){
      cell_start[cell_i] = element_num;
      ++cell_i;
    }
    std::cout<<"Calculating sizes"<<std::endl;
    for(size_t i =0;i<cell_num-1;++i){
      cell_size[i] = cell_start[i+1]-cell_start[i];
    }
    cell_size[cell_num-1] = element_num - cell_start[cell_num-1];
    std::cout<<"deleting srt"<<std::endl;
    delete [] srt;
    std::cout<<"done"<<std::endl;
  }
  
  size_t ChainingMeshIndex::get_cell_id_from_position(float* xyz){
    size_t ijk[dim_num];
    for(int i=0;i<dim_num;++i)
      ijk[i] = xyz[i]/cell_length_xyz[i];
    return get_cell_id_from_indexes(ijk);
  }
  size_t ChainingMeshIndex::get_cell_id_from_indexes(size_t* ijk){
    size_t cell_id = 0;
    for(int i =0;i<dim_num;++i){
      cell_id += cell_ijk_offset[i]*ijk[i];
    }
    return cell_id;
  }
  void ChainingMeshIndex::get_indexes_from_cell_id(size_t cell_id, size_t* output_ijk){
    for(int i =0;i<dim_num;++i){
      output_ijk[i] = cell_id/cell_ijk_offset[i];
      cell_id = cell_id%cell_ijk_offset[i];
    }
  }
  void ChainingMeshIndex::get_indexes_from_position(float* xyz, size_t* output_ijk){
    size_t cell_id  = get_cell_id_from_position(xyz);
    get_indexes_from_cell_id(cell_id, output_ijk);
  }
  void ChainingMeshIndex::get_cell_element_indexes(size_t cell_index, size_t*& cell_element_start, size_t& cell_element_size){
    cell_element_start = element_index+cell_start[cell_index];
    cell_element_size = cell_size[cell_index];
  }
  std::vector<size_t> ChainingMeshIndex::get_region_cell_id_list(size_t cell_id, size_t length){
    size_t ijk[dim_num];
    get_indexes_from_cell_id(cell_id, ijk);
    return get_region_cell_id_list(ijk, length);
  }
  std::vector<size_t> ChainingMeshIndex::get_region_cell_id_list(size_t* ijk, size_t length){
    std::vector<size_t> cell_id_neighbor;
    int ijk_offset[dim_num];
    int ijk_neighbor[dim_num];
    int n_side = 2*length +1;
    size_t total_neighbors = 1;
    for(int i =0;i<dim_num;++i){
      ijk_offset[i] = -length;
      // std::cout<<total_neighbors<<std::endl; 
      total_neighbors *= n_side;
      // std::cout<<total_neighbors<<std::endl;
    }
    // std::cout<<"ijk: "<<ijk[0]<<" "<<ijk[1]<<std::endl;
    // std::cout<<"ijk_neigh: "<<ijk_neighbor[0]<<" "<<ijk_neighbor[1]<<std::endl;
    // std::cout<<"neigb num: "<<total_neighbors<<std::endl;
    //std::cout<<"Total neighbors: "<<total_neighbors<<std::endl;
    ijk_offset[0]-=1; //first neighbor to add is the corner
    for(int i =0;i<total_neighbors;++i){
      // std::cout<<"\noffset: ";
      // for(int j =0;j<dim_num;++j)
      // 	std::cout<<ijk_offset[j]<<" ";
      // std::cout<<std::endl;
      ijk_offset[0]+=1;
      for(int j =0;j<dim_num;++j){
	if(ijk_offset[j] > static_cast<int64_t>(length)){
	  //std::cout<<ijk_offset[j]<<" > "<<length<<" = "<<(ijk_offset[j] > static_cast<int64_t>(length))<<std::endl;
	  //	  std::cout<<"++"<<std::endl;
	  ijk_offset[j+1] += 1;
	  ijk_offset[j] = -length;
	}
	ijk_neighbor[j]=static_cast<int>(ijk[j])+ijk_offset[j];
      }
      // std::cout<<"offset: ";
      // for(int j =0;j<dim_num;++j)
      // 	std::cout<<ijk_offset[j]<<" ";
      // std::cout<<std::endl;
      // std::cout<<"neighbor ijk: ";
      // for(int j =0;j<dim_num;++j)
      // 	std::cout<<ijk_neighbor[j]<<" ";
      // std::cout<<std::endl;
      cell_id_neighbor.push_back(get_cell_id_from_indexes_wrap(ijk_neighbor));
    }
    return cell_id_neighbor;
  }
  std::vector<size_t> ChainingMeshIndex::get_region_cell_id_list(float* xyz, float radius){
    int ijk_min[dim_num];
    int ijk_max[dim_num];
    int ijk_tmp[dim_num];
    float xyz_tmp[dim_num];
    size_t total_possible_neighbors =1;
    std::set<size_t> result_set;
    for(int i =0;i<dim_num;++i){
      ijk_min[i] = (xyz[i]-radius)/cell_length_xyz[i];
      ijk_max[i] = (xyz[i]+radius)/cell_length_xyz[i]+1;
      total_possible_neighbors *=(ijk_max[i]-ijk_min[i]+1);
      std::cout<<ijk_min[i]<<" -> "<<ijk_max[i]<<std::endl;
    }
    std::copy(ijk_min, ijk_min+dim_num, ijk_tmp);
    ijk_tmp[0]-=1;
    for(int ii=0;ii<total_possible_neighbors;++ii){
      ijk_tmp[0]+=1;
      for(int i=0;i<dim_num;++i){
    	if(ijk_tmp[i]==ijk_max[i]){
	  
    	  ijk_tmp[i]=ijk_min[i];
    	  ijk_tmp[i+1]+=1;
    	}
      }
      result_set.insert(get_cell_id_from_indexes_wrap(ijk_tmp));
    }
    std::vector<size_t> result(result_set.begin(), result_set.end());
    return result;
  }

  std::vector<size_t> ChainingMeshIndex::query_elements_within(float* target_xyz, float radius){
    size_t neighbors_to_check = 0;
    for(int i =0;i<dim_num;++i){
      size_t len = (radius/cell_length_xyz[i])+1.0;
      if(len > neighbors_to_check)
	neighbors_to_check = len;
    }
    // std::cout<<"neighbors to check: "<<neighbors_to_check<<std::endl;
    std::vector<size_t> cells = get_region_cell_id_list(get_cell_id_from_position(target_xyz), neighbors_to_check);
    // std::cout<<"cells size: "<<cells.size()<<std::endl;
    std::vector<size_t> elements_within;
    size_t* cell_elements_index;
    size_t  cell_elements_num;
    float element_xyz[3];
    for(int i =0;i<cells.size();++i){
      // std::cout<<"Starting on cell: "<<i<<std::endl;
      get_cell_element_indexes(cells[i], cell_elements_index, cell_elements_num);
      // std::cout<<"cell: "<<cells[i]<<" cell_elments_num: "<<cell_elements_num<<"\t\t"<<cell_elements_index[0]<<std::endl;
      for(int j=0;j<cell_elements_num;++j){
	copy_point(element_positions, cell_elements_index[j], element_xyz);
	float rad = calculate_periodic_distance(target_xyz, element_xyz);
	if(rad < radius)
	  elements_within.push_back(cell_elements_index[j]);
      }
    }
    return elements_within;
  }
  float ChainingMeshIndex::calculate_periodic_distance(float* xyz1, float *xyz2){
    float dist =0;
    for(int i =0;i<dim_num;++i){
      float dx = fmod(fabs(xyz1[i] - xyz2[i]), length_xyz[i]);
      if(dx > length_xyz[i]/2.0)
      	dx = length_xyz[i]-dx;
      dist += dx*dx;
    }
    return std::sqrt(dist);
  }
  void ChainingMeshIndex::copy_point(float** xyz, size_t index, float* xyz_dest){
    for(int i =0;i<dim_num;++i)
      xyz_dest[i] = xyz[i][index];
  }
}
