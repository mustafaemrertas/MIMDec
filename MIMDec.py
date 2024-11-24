import hashlib
import itertools
import string
import time
import os
from concurrent.futures import ProcessPoolExecutor
from colorama import init, Fore, Style

# Colorama'yı başlat
init(autoreset=True)

ASCII_ART = f"""
{Fore.CYAN}

 ****     **** ** ****     **** *******                  
/**/**   **/**/**/**/**   **/**/**////**                 
/**//** ** /**/**/**//** ** /**/**    /**  *****   ***** 
/** //***  /**/**/** //***  /**/**    /** **///** **///**
/**  //*   /**/**/**  //*   /**/**    /**/*******/**  // 
/**   /    /**/**/**   /    /**/**    ** /**//// /**   **
/**        /**/**/**        /**/*******  //******//***** 
//         // // //         // ///////    //////  /////   

"""

def hash_check(guess, target_hash, hash_type):
    """Hash doğrulama fonksiyonu."""
    hash_func = getattr(hashlib, hash_type)
    return hash_func(guess.encode()).hexdigest() == target_hash

def brute_force_task(args):
    """Brute force işlemi için alt görev."""
    target_hash, hash_type, characters, length, offset, total_workers = args
    combinations = itertools.product(characters, repeat=length)
    for index, attempt in enumerate(combinations):
        if index % total_workers == offset:  # İşçiye özel kombinasyon hesaplaması
            guess = ''.join(attempt)
            if hash_check(guess, target_hash, hash_type):
                return guess
    return None

def main():
    print(ASCII_ART)
    print(f"{Fore.CYAN}{Style.BRIGHT}MIMDec - Powerful Hash Decryptor")
    print(f"{Fore.CYAN}{Style.BRIGHT}-----------------------------------")

    user_hash = input(f"{Fore.YELLOW}Hash değerini giriniz: ")
    hash_type = input(f"{Fore.YELLOW}Hash türünü giriniz (md5, sha1, sha256): ").lower()
    
    # Karakter kümesini oluştur
    characters = string.ascii_letters + string.digits + "." # Yalnızca alfanümerik karakterler

    while True:
        try:
            min_length = int(input(f"{Fore.YELLOW}Başlangıç uzunluğunu giriniz (örn: 1): "))
            max_length = int(input(f"{Fore.YELLOW}Bitirilecek uzunluğu giriniz (örn: 4): "))
            if min_length > 0 and max_length >= min_length:
                break
            else:
                print(f"{Fore.RED}Lütfen geçerli bir aralık giriniz.")
        except ValueError:
            print(f"{Fore.RED}Geçerli bir sayı giriniz.")

    start_time = time.time()
    found_value = None
    attempts = 0

    # Donanımdaki çekirdek sayısını alma
    total_cpu_cores = os.cpu_count() or 4  # CPU çekirdek sayısını alıyoruz

    # İşlem havuzunu oluşturma
    with ProcessPoolExecutor(max_workers=total_cpu_cores) as executor:
        for length in range(min_length, max_length + 1):
            print(f"{Fore.GREEN}\n{length} karakter uzunluğunda kombinasyonlar deneniyor...")

            total_workers = min(total_cpu_cores, executor._max_workers)
            tasks = [(user_hash, hash_type, characters, length, i, total_workers) for i in range(total_workers)]
            results = executor.map(brute_force_task, tasks)

            # Sonuçları kontrol et
            for result in results:
                if result:
                    found_value = result
                    break

            # Anlık durum bilgisi
            attempts += len(characters) ** length * total_workers
            elapsed_time = time.time() - start_time
            print(f"{Fore.YELLOW}Denenen değerler: {attempts} | Geçen Süre: {elapsed_time:.2f} saniye")
            
            if found_value:
                break

    elapsed_time = time.time() - start_time
    if found_value:
        print(f'\n{Fore.BLUE}Bulunan değer: {found_value}')
    else:
        print(f"{Fore.RED}Hash çözümü bulunamadı.")

    print(f"{Fore.MAGENTA}Toplam süre: {elapsed_time:.2f} saniye")

if __name__ == "__main__":
    main()